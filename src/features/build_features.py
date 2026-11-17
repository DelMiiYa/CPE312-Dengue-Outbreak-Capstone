"""Feature engineering, outbreak label creation, time split, and summary generation.

This module processes data/processed/panel.csv into:
1. data/processed/province_thresholds.csv (per-province baseline & threshold fit on train years only)
2. data/processed/modeling_table.csv (leak-free modeling table ready for supervised learning)
3. results/feature_summary.json (class balance, split metadata, dropped-row accounting)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml


def load_params(config_path: str | Path = "config/params.yaml") -> dict[str, Any]:
    """Load configuration parameters from YAML file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def verify_panel_continuity(panel: pd.DataFrame) -> None:
    """Verify that each province has a continuous, gap-free monthly sequence.

    Args:
        panel: DataFrame containing panel data.

    Raises:
        ValueError: If any province has missing months or irregular time steps.
    """
    required_cols = [
        "province_en",
        "year",
        "month",
        "cases",
        "temp_mean_c",
        "precip_sum_mm",
        "humidity_mean_pct",
    ]
    missing = [c for c in required_cols if c not in panel.columns]
    if missing:
        raise ValueError(f"Panel is missing required columns: {missing}")

    # Check for consecutive monthly sequence per province
    for prov, group in panel.groupby("province_en"):
        dates = pd.to_datetime(
            group["year"].astype(str) + "-" + group["month"].astype(str).str.zfill(2) + "-01"
        )
        if not dates.is_monotonic_increasing:
            raise ValueError(f"Dates for province '{prov}' are not strictly monotonic increasing.")
        expected_range = pd.date_range(dates.iloc[0], dates.iloc[-1], freq="MS")
        if len(dates) != len(expected_range) or not (dates.values == expected_range.values).all():
            raise ValueError(f"Province '{prov}' has missing or irregular monthly dates.")


def compute_province_thresholds(
    panel: pd.DataFrame,
    params: dict[str, Any],
) -> pd.DataFrame:
    """Compute per-province historical mean, std, and outbreak threshold on train years only.

    Threshold formula: threshold_p = mean_p + k * sd_p
    Fitted strictly on train years (e.g. 1993-2015) using non-null cases.

    Args:
        panel: DataFrame of monthly province observations.
        params: Configuration dictionary containing split.train_years and outbreak_k.

    Returns:
        DataFrame with columns: province_en, train_months, mean_p, sd_p, threshold_p
    """
    train_start, train_end = params["split"]["train_years"]
    outbreak_k = float(params.get("outbreak_k", 1.0))

    train_mask = (
        (panel["year"] >= train_start)
        & (panel["year"] <= train_end)
        & panel["cases"].notna()
    )
    train_slice = panel[train_mask]

    thresholds = (
        train_slice.groupby("province_en")["cases"]
        .agg(
            train_months="count",
            mean_p="mean",
            sd_p=lambda s: float(s.std(ddof=1)),
        )
        .reset_index()
    )

    thresholds["threshold_p"] = thresholds["mean_p"] + outbreak_k * thresholds["sd_p"]
    thresholds = thresholds.sort_values("province_en").reset_index(drop=True)

    # Validate output
    if thresholds.isna().any().any():
        raise ValueError("Computed thresholds contain NaNs.")
    if (thresholds["sd_p"] <= 0).any():
        raise ValueError("Found province with non-positive standard deviation.")

    return thresholds


def build_modeling_table(
    panel: pd.DataFrame,
    thresholds: pd.DataFrame,
    params: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    """Build leak-free supervised modeling table and identify dropped rows.

    Features at row (p, t) use strictly data up to month t.
    Target at row (p, t) is outbreak_t1 at month t+1.
    Splits are assigned by target_year so evaluation sets contain full calendar years.

    Args:
        panel: Panel dataset.
        thresholds: Province thresholds fit on train years only.
        params: Configuration dictionary.

    Returns:
        Tuple of (clean_modeling_df, dropped_df, feature_columns).
    """
    df = panel.copy()
    df = df.sort_values(["province_en", "year", "month"]).reset_index(drop=True)
    verify_panel_continuity(df)

    # Merge train-only province parameters
    thresh_cols = ["province_en", "mean_p", "sd_p", "threshold_p"]
    df = df.merge(thresholds[thresh_cols], on="province_en", how="left")

    # 1. Target definition at month t+1
    # Calendar arithmetic for target month/year
    df["target_year"] = np.where(df["month"] == 12, df["year"] + 1, df["year"])
    df["target_month"] = np.where(df["month"] == 12, 1, df["month"] + 1)
    df["target_cases_t1"] = df.groupby("province_en")["cases"].shift(-1)
    df["outbreak_t1"] = np.where(
        df["target_cases_t1"].isna(),
        np.nan,
        (df["target_cases_t1"] > df["threshold_p"]).astype(float),
    )

    # 2. Case features (strictly month <= t)
    df["cases_lag_0"] = df["cases"]
    case_lags = params.get("features", {}).get("case_lags", [1, 2, 3])
    for k in case_lags:
        df[f"cases_lag_{k}"] = df.groupby("province_en")["cases"].shift(k)

    roll_window = params.get("features", {}).get("case_rolling_window", 3)
    df["cases_roll_mean_3"] = df.groupby("province_en")["cases"].transform(
        lambda s: s.rolling(roll_window, min_periods=roll_window).mean()
    )
    df["cases_zscore_lag_0"] = (df["cases_lag_0"] - df["mean_p"]) / df["sd_p"]

    # 3. Baseline helper features (strictly month <= t)
    # outbreak_lag_0: current month outbreak status ("same flag as this month" baseline)
    df["outbreak_lag_0"] = np.where(
        df["cases_lag_0"].isna(),
        np.nan,
        (df["cases_lag_0"] > df["threshold_p"]).astype(float),
    )
    # outbreak_same_month_last_year: month (t+1) - 12 = t - 11
    cases_lag_11 = df.groupby("province_en")["cases"].shift(11)
    df["outbreak_same_month_last_year"] = np.where(
        cases_lag_11.isna(),
        np.nan,
        (cases_lag_11 > df["threshold_p"]).astype(float),
    )

    # 4. Weather lag features (strictly month <= t)
    weather_lags = params.get("features", {}).get("weather_lags", [0, 1, 2, 3])
    for k in weather_lags:
        df[f"temp_lag_{k}"] = df.groupby("province_en")["temp_mean_c"].shift(k)
        df[f"precip_lag_{k}"] = df.groupby("province_en")["precip_sum_mm"].shift(k)
        df[f"humidity_lag_{k}"] = df.groupby("province_en")["humidity_mean_pct"].shift(k)

    # 5. Calendar encoding
    df["sin_target_month"] = np.sin(2.0 * np.pi * df["target_month"] / 12.0)
    df["cos_target_month"] = np.cos(2.0 * np.pi * df["target_month"] / 12.0)

    # 6. Split assignment by target_year
    train_years = params["split"]["train_years"]
    val_years = params["split"]["val_years"]
    test_years = params["split"]["test_years"]
    normal_years = params["split"]["test_subperiods"]["normal"]
    covid_years = params["split"]["test_subperiods"]["covid"]

    def assign_split(target_yr: int) -> str:
        if train_years[0] <= target_yr <= train_years[1]:
            return "train"
        if val_years[0] <= target_yr <= val_years[1]:
            return "val"
        if test_years[0] <= target_yr <= test_years[1]:
            return "test"
        return "other"

    df["split"] = df["target_year"].apply(assign_split)

    def assign_subperiod(row: pd.Series) -> str:
        if row["split"] == "test":
            if normal_years[0] <= row["target_year"] <= normal_years[1]:
                return "normal"
            if covid_years[0] <= row["target_year"] <= covid_years[1]:
                return "covid"
        return "none"

    df["subperiod"] = df.apply(assign_subperiod, axis=1)

    # Column catalog
    feature_columns = [
        "cases_lag_0",
        "cases_lag_1",
        "cases_lag_2",
        "cases_lag_3",
        "cases_roll_mean_3",
        "cases_zscore_lag_0",
        "outbreak_lag_0",
        "outbreak_same_month_last_year",
        "temp_lag_0",
        "temp_lag_1",
        "temp_lag_2",
        "temp_lag_3",
        "precip_lag_0",
        "precip_lag_1",
        "precip_lag_2",
        "precip_lag_3",
        "humidity_lag_0",
        "humidity_lag_1",
        "humidity_lag_2",
        "humidity_lag_3",
        "month",
        "target_month",
        "sin_target_month",
        "cos_target_month",
        "mean_p",
        "sd_p",
        "threshold_p",
    ]

    id_columns = [
        "province_en",
        "year",
        "month",
        "target_year",
        "target_month",
        "split",
        "subperiod",
    ]
    target_columns = ["target_cases_t1", "outbreak_t1"]

    ordered_columns = [
        "province_en",
        "year",
        "month",
        "target_year",
        "target_month",
        "split",
        "subperiod",
        "cases_lag_0",
        "cases_lag_1",
        "cases_lag_2",
        "cases_lag_3",
        "cases_roll_mean_3",
        "cases_zscore_lag_0",
        "outbreak_lag_0",
        "outbreak_same_month_last_year",
        "temp_lag_0",
        "temp_lag_1",
        "temp_lag_2",
        "temp_lag_3",
        "precip_lag_0",
        "precip_lag_1",
        "precip_lag_2",
        "precip_lag_3",
        "humidity_lag_0",
        "humidity_lag_1",
        "humidity_lag_2",
        "humidity_lag_3",
        "sin_target_month",
        "cos_target_month",
        "mean_p",
        "sd_p",
        "threshold_p",
        "target_cases_t1",
        "outbreak_t1",
    ]

    # Row filtering: drop any row where outbreak_t1 or any feature is NaN
    nan_mask = df[ordered_columns].isna().any(axis=1)
    dropped_df = df[nan_mask].copy()
    clean_df = df[~nan_mask][ordered_columns].copy()

    # Cast integer columns
    int_cols = [
        "year",
        "month",
        "target_year",
        "target_month",
        "outbreak_lag_0",
        "outbreak_same_month_last_year",
        "outbreak_t1",
    ]
    for col in int_cols:
        clean_df[col] = clean_df[col].astype(int)

    clean_df = clean_df.sort_values(["province_en", "year", "month"]).reset_index(drop=True)
    return clean_df, dropped_df, feature_columns


def generate_feature_summary(
    panel: pd.DataFrame,
    modeling_df: pd.DataFrame,
    dropped_df: pd.DataFrame,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Generate detailed feature summary, split statistics, and dropped-row accounting."""
    total_panel_rows = len(panel)
    modeling_rows = len(modeling_df)
    total_dropped = len(dropped_df)

    # Detailed dropped row breakdown
    # 1. 2022-12 end of series (missing target at 2023-01)
    end_of_series = dropped_df[(dropped_df["year"] == 2022) & (dropped_df["month"] == 12)]
    # 2. Late starting provinces pre-establishment
    late_4 = ["Amnat Charoen", "Mukdahan", "Nong Bua Lamphu", "Sa Kaeo"]
    late_4_pre = dropped_df[
        dropped_df["province_en"].isin(late_4) & (dropped_df["year"] < 2003)
    ]
    late_4_initial_lags = dropped_df[
        dropped_df["province_en"].isin(late_4)
        & (dropped_df["year"] == 2003)
        & (dropped_df["month"] <= 11)
    ]
    bueng_kan_pre = dropped_df[
        (dropped_df["province_en"] == "Bueng Kan") & (dropped_df["year"] < 2011)
    ]
    bueng_kan_initial_lags = dropped_df[
        (dropped_df["province_en"] == "Bueng Kan")
        & (dropped_df["year"] == 2011)
        & (dropped_df["month"] <= 11)
    ]
    regular_initial_lags = dropped_df[
        ~dropped_df["province_en"].isin(late_4 + ["Bueng Kan"])
        & (dropped_df["year"] == 1993)
        & (dropped_df["month"] <= 11)
    ]

    dropped_accounting = {
        "total_dropped": total_dropped,
        "breakdown": {
            "initial_lags_regular_provinces": {
                "count": int(len(regular_initial_lags)),
                "description": (
                    "72 regular provinces x 11 months (1993-01 to 1993-11) missing "
                    "11-month lag for outbreak_same_month_last_year"
                ),
            },
            "late_starting_provinces_pre_start": {
                "count": int(len(late_4_pre)),
                "description": (
                    "4 late provinces (Amnat Charoen, Mukdahan, Nong Bua Lamphu, Sa Kaeo) "
                    "x 120 months (1993-01 to 2002-12) unestablished"
                ),
            },
            "late_starting_provinces_initial_lags": {
                "count": int(len(late_4_initial_lags)),
                "description": (
                    "4 late provinces x 11 months (2003-01 to 2003-11) missing "
                    "11-month lag for outbreak_same_month_last_year"
                ),
            },
            "bueng_kan_pre_start": {
                "count": int(len(bueng_kan_pre)),
                "description": "Bueng Kan x 216 months (1993-01 to 2010-12) unestablished",
            },
            "bueng_kan_initial_lags": {
                "count": int(len(bueng_kan_initial_lags)),
                "description": (
                    "Bueng Kan x 11 months (2011-01 to 2011-11) missing "
                    "11-month lag for outbreak_same_month_last_year"
                ),
            },
            "end_of_series_missing_target": {
                "count": int(len(end_of_series)),
                "description": "77 provinces x 1 month (2022-12) missing target month 2023-01",
            },
        },
    }

    # Split summaries
    splits_summary: dict[str, Any] = {}
    for split_name in ["train", "val", "test"]:
        sub_df = modeling_df[modeling_df["split"] == split_name]
        pos_count = int(sub_df["outbreak_t1"].sum())
        total_count = len(sub_df)
        splits_summary[split_name] = {
            "rows": total_count,
            "provinces": int(sub_df["province_en"].nunique()),
            "min_target_year": int(sub_df["target_year"].min()),
            "max_target_year": int(sub_df["target_year"].max()),
            "outbreak_count": pos_count,
            "non_outbreak_count": total_count - pos_count,
            "prevalence": float(pos_count / total_count if total_count > 0 else 0.0),
        }

    # Test subperiod summaries
    for subperiod_name in ["normal", "covid"]:
        sub_df = modeling_df[
            (modeling_df["split"] == "test") & (modeling_df["subperiod"] == subperiod_name)
        ]
        pos_count = int(sub_df["outbreak_t1"].sum())
        total_count = len(sub_df)
        label = (
            "test_normal_2018_2019"
            if subperiod_name == "normal"
            else "test_covid_2020_2022"
        )
        splits_summary[label] = {
            "rows": total_count,
            "provinces": int(sub_df["province_en"].nunique()),
            "min_target_year": int(sub_df["target_year"].min()),
            "max_target_year": int(sub_df["target_year"].max()),
            "outbreak_count": pos_count,
            "non_outbreak_count": total_count - pos_count,
            "prevalence": float(pos_count / total_count if total_count > 0 else 0.0),
        }

    return {
        "total_panel_rows": total_panel_rows,
        "modeling_table_rows": modeling_rows,
        "total_dropped_rows": total_dropped,
        "dropped_rows_accounting": dropped_accounting,
        "splits": splits_summary,
        "feature_columns": feature_columns,
        "target_column": "outbreak_t1",
    }


def main() -> None:
    """Run full feature and label engineering pipeline."""
    params = load_params()

    panel_path = Path("data/processed/panel.csv")
    if not panel_path.exists():
        raise FileNotFoundError(f"Processed panel not found: {panel_path}")

    print(f"Reading panel data from {panel_path}...")
    panel = pd.read_csv(panel_path)
    print(f"Panel loaded: {panel.shape[0]} rows, {panel['province_en'].nunique()} provinces.")

    print("Computing province thresholds fit strictly on train years...")
    thresholds = compute_province_thresholds(panel, params)
    thresholds_out = Path("data/processed/province_thresholds.csv")
    thresholds_out.parent.mkdir(parents=True, exist_ok=True)
    thresholds.to_csv(thresholds_out, index=False)
    print(f"Saved {thresholds.shape[0]} province thresholds to {thresholds_out}")

    print("Building supervised modeling table...")
    modeling_df, dropped_df, feature_cols = build_modeling_table(panel, thresholds, params)
    modeling_out = Path("data/processed/modeling_table.csv")
    modeling_df.to_csv(modeling_out, index=False)
    print(f"Saved modeling table with shape {modeling_df.shape} to {modeling_out}")

    print("Generating feature summary and class balance report...")
    summary = generate_feature_summary(panel, modeling_df, dropped_df, feature_cols)
    summary_out = Path("results/feature_summary.json")
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved feature summary to {summary_out}")

    # Also update metrics.json to track official numbers
    metrics_path = Path(params.get("paths", {}).get("metrics_json", "results/metrics.json"))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_data = {}
    if metrics_path.exists():
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            metrics_data = {}

    metrics_data["dataset"] = {
        "total_panel_rows": summary["total_panel_rows"],
        "modeling_rows": summary["modeling_table_rows"],
        "dropped_rows": summary["total_dropped_rows"],
        "splits": summary["splits"],
    }
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Updated dataset summary in {metrics_path}")

    # Display console summary matching acceptance criterion 2
    print("\n--- Pipeline Summary ---")
    agg_table = modeling_df.groupby("split").agg(
        rows=("outbreak_t1", "size"),
        provs=("province_en", "nunique"),
        min_ty=("target_year", "min"),
        max_ty=("target_year", "max"),
        pos_rate=("outbreak_t1", "mean"),
    ).round(4)
    print(agg_table)
    print("------------------------\n")


if __name__ == "__main__":
    main()
