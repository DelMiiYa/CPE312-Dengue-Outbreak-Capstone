"""
Exploratory Data Analysis (EDA) module for Thailand dengue outbreak prediction.

Generates publication-ready figures and numerical statistics from data/processed/panel.csv
to support poster section R3 (and visual evidence for R1, R2).

Figures generated:
1. results/figures/eda_seasonality.png: Monthly seasonal profile of dengue cases alongside rainfall and temperature.
2. results/figures/eda_lag_correlation.png: Lag correlations (lags 0-4) between weather variables and dengue cases (train years only).
3. results/figures/eda_province_heterogeneity.png: Case distributions across provinces demonstrating baseline heterogeneity.
4. results/figures/eda_annual_trend_covid.png: Annual total cases and zero-case share (1993-2022) showing epidemic peaks and COVID drop.

Output statistics:
- results/eda_stats.json: All numerical statistics cited in eda_summary.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def load_config_and_data(
    config_path: str = "config/params.yaml",
    panel_path: str = "data/processed/panel.csv",
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Load project config and panel dataset."""
    cfg_file = Path(config_path)
    if not cfg_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    data_file = Path(panel_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Panel data file not found: {panel_path}")
    df = pd.read_csv(data_file)

    # Sort strictly by province and time
    df = df.sort_values(["province_en", "year", "month"]).reset_index(drop=True)
    return cfg, df


def compute_seasonality_stats(
    df: pd.DataFrame, train_years: Tuple[int, int]
) -> Dict[str, Any]:
    """
    Compute monthly seasonal averages for dengue cases, precipitation,
    temperature, and humidity strictly on train years (1993-2015).
    """
    start_yr, end_yr = train_years
    train_mask = (df["year"] >= start_yr) & (df["year"] <= end_yr)
    df_train = df[train_mask].copy()

    monthly = (
        df_train.groupby("month")
        .agg(
            mean_cases=("cases", "mean"),
            median_cases=("cases", "median"),
            std_cases=("cases", "std"),
            sem_cases=("cases", "sem"),
            total_cases=("cases", "sum"),
            mean_precip_mm=("precip_sum_mm", "mean"),
            std_precip_mm=("precip_sum_mm", "std"),
            mean_temp_c=("temp_mean_c", "mean"),
            std_temp_c=("temp_mean_c", "std"),
            mean_humidity_pct=("humidity_mean_pct", "mean"),
            std_humidity_pct=("humidity_mean_pct", "std"),
            valid_province_months=("cases", "count"),
        )
        .reset_index()
    )

    monthly_records = []
    for _, row in monthly.iterrows():
        monthly_records.append(
            {
                "month": int(row["month"]),
                "mean_cases": round(float(row["mean_cases"]), 2),
                "median_cases": round(float(row["median_cases"]), 2),
                "std_cases": round(float(row["std_cases"]), 2),
                "sem_cases": round(float(row["sem_cases"]), 2),
                "total_cases": int(row["total_cases"]),
                "mean_precip_mm": round(float(row["mean_precip_mm"]), 2),
                "mean_temp_c": round(float(row["mean_temp_c"]), 2),
                "mean_humidity_pct": round(float(row["mean_humidity_pct"]), 2),
                "valid_province_months": int(row["valid_province_months"]),
            }
        )

    peak_case_row = monthly.loc[monthly["mean_cases"].idxmax()]
    trough_case_row = monthly.loc[monthly["mean_cases"].idxmin()]
    peak_temp_row = monthly.loc[monthly["mean_temp_c"].idxmax()]
    peak_precip_row = monthly.loc[monthly["mean_precip_mm"].idxmax()]

    stats = {
        "monthly_profile": monthly_records,
        "peak_dengue_month": int(peak_case_row["month"]),
        "peak_dengue_mean_cases": round(float(peak_case_row["mean_cases"]), 2),
        "peak_dengue_median_cases": round(float(peak_case_row["median_cases"]), 2),
        "trough_dengue_month": int(trough_case_row["month"]),
        "trough_dengue_mean_cases": round(float(trough_case_row["mean_cases"]), 2),
        "trough_dengue_median_cases": round(float(trough_case_row["median_cases"]), 2),
        "peak_temp_month": int(peak_temp_row["month"]),
        "peak_temp_mean_c": round(float(peak_temp_row["mean_temp_c"]), 2),
        "peak_precip_month": int(peak_precip_row["month"]),
        "peak_precip_mean_mm": round(float(peak_precip_row["mean_precip_mm"]), 2),
        "monsoon_onset_month": 5,
        "monsoon_onset_mean_precip_mm": round(
            float(monthly.loc[monthly["month"] == 5, "mean_precip_mm"].iloc[0]), 2
        ),
    }
    return stats


def compute_lag_correlation_stats(
    df: pd.DataFrame, train_years: Tuple[int, int], max_lag: int = 4
) -> Dict[str, Any]:
    """
    Compute lag correlations (lags 0 to 4) between weather variables and cases.
    Weather lags are created strictly within each province: groupby('province_en').shift(k).
    Then filtered to train years (1993-2015).
    Computes:
    - Median within-province Pearson correlation across the 77 provinces
    - 25th and 75th percentiles (IQR) across provinces
    - Pooled Pearson correlation using log1p(cases)
    - Pooled Pearson correlation using province-standardized cases (z-scores)
    - Pooled Pearson correlation using raw cases
    """
    start_yr, end_yr = train_years
    weather_vars = ["precip_sum_mm", "temp_mean_c", "humidity_mean_pct"]

    # Compute lags within province
    df_lags = df.copy()
    for var in weather_vars:
        for k in range(0, max_lag + 1):
            df_lags[f"{var}_lag_{k}"] = df_lags.groupby("province_en")[var].shift(k)

    # Filter strictly to train years
    train_mask = (df_lags["year"] >= start_yr) & (df_lags["year"] <= end_yr)
    df_train = df_lags[train_mask].copy()

    # Precompute province z-score and log1p cases for pooled analysis
    df_train["cases_log1p"] = np.log1p(df_train["cases"])
    df_train["cases_zscore"] = df_train.groupby("province_en")["cases"].transform(
        lambda s: (s - s.mean()) / (s.std() + 1e-9)
    )

    stats: Dict[str, Any] = {}
    for var in weather_vars:
        var_stats = []
        for k in range(0, max_lag + 1):
            col = f"{var}_lag_{k}"

            # Within-province correlations
            prov_corrs = []
            for _, grp in df_train.groupby("province_en"):
                sub = grp[["cases", col]].dropna()
                if len(sub) > 10:
                    r = sub["cases"].corr(sub[col])
                    if not np.isnan(r):
                        prov_corrs.append(r)

            median_r = float(np.median(prov_corrs)) if prov_corrs else float("nan")
            q25_r = float(np.percentile(prov_corrs, 25)) if prov_corrs else float("nan")
            q75_r = float(np.percentile(prov_corrs, 75)) if prov_corrs else float("nan")

            # Pooled log1p
            sub_log = df_train[["cases_log1p", col]].dropna()
            pooled_log1p = float(sub_log["cases_log1p"].corr(sub_log[col]))

            # Pooled z-score
            sub_z = df_train[["cases_zscore", col]].dropna()
            pooled_zscore = float(sub_z["cases_zscore"].corr(sub_z[col]))

            # Pooled raw
            sub_raw = df_train[["cases", col]].dropna()
            pooled_raw = float(sub_raw["cases"].corr(sub_raw[col]))

            var_stats.append(
                {
                    "lag": k,
                    "median_within_province": round(median_r, 4),
                    "q25_within_province": round(q25_r, 4),
                    "q75_within_province": round(q75_r, 4),
                    "pooled_log1p": round(pooled_log1p, 4),
                    "pooled_zscore": round(pooled_zscore, 4),
                    "pooled_raw": round(pooled_raw, 4),
                }
            )
        stats[var] = var_stats

    return stats


def compute_province_heterogeneity_stats(
    df: pd.DataFrame, train_years: Tuple[int, int]
) -> Dict[str, Any]:
    """
    Compute distribution of cases across all 77 provinces on train years (1993-2015).
    Demonstrates baseline variance and proves why local threshold (mean_p + 1*SD_p)
    is necessary over a single national threshold.
    """
    start_yr, end_yr = train_years
    train_mask = (df["year"] >= start_yr) & (df["year"] <= end_yr)
    df_train = df[train_mask].copy()

    # National baseline on train set
    national_mean = float(df_train["cases"].mean())
    national_std = float(df_train["cases"].std())
    national_threshold = national_mean + 1.0 * national_std

    prov_agg = (
        df_train.groupby("province_en")["cases"]
        .agg(
            count="count",
            mean="mean",
            std="std",
            median="median",
            min="min",
            max="max",
        )
        .reset_index()
    )
    prov_agg["threshold"] = prov_agg["mean"] + 1.0 * prov_agg["std"]
    prov_agg = prov_agg.sort_values("mean", ascending=False).reset_index(drop=True)

    top_5 = []
    for _, r in prov_agg.head(5).iterrows():
        top_5.append(
            {
                "province_en": str(r["province_en"]),
                "mean": round(float(r["mean"]), 2),
                "std": round(float(r["std"]), 2),
                "median": round(float(r["median"]), 2),
                "max": round(float(r["max"]), 2),
                "threshold": round(float(r["threshold"]), 2),
            }
        )

    bottom_5 = []
    for _, r in prov_agg.tail(5).iloc[::-1].iterrows():  # lowest first
        bottom_5.append(
            {
                "province_en": str(r["province_en"]),
                "mean": round(float(r["mean"]), 2),
                "std": round(float(r["std"]), 2),
                "median": round(float(r["median"]), 2),
                "max": round(float(r["max"]), 2),
                "threshold": round(float(r["threshold"]), 2),
            }
        )

    # Provinces whose historical maximum cases in train never reaches national threshold
    never_reach_national = prov_agg[prov_agg["max"] < national_threshold][
        "province_en"
    ].tolist()

    highest_p = top_5[0]
    lowest_p = bottom_5[0]
    ratio_top_to_bottom = round(highest_p["mean"] / lowest_p["mean"], 2)
    ratio_highest_to_national = round(highest_p["mean"] / national_mean, 2)

    return {
        "train_years": list(train_years),
        "national_mean_cases": round(national_mean, 2),
        "national_std_cases": round(national_std, 2),
        "national_threshold_mean_plus_1sd": round(national_threshold, 2),
        "highest_province": highest_p,
        "lowest_province": lowest_p,
        "ratio_top_to_bottom_mean": ratio_top_to_bottom,
        "ratio_highest_to_national_mean": ratio_highest_to_national,
        "top_5_provinces": top_5,
        "bottom_5_provinces": bottom_5,
        "provinces_never_reaching_national_threshold_count": len(never_reach_national),
        "provinces_never_reaching_national_threshold_list": sorted(never_reach_national),
    }


def compute_annual_trend_stats(
    df: pd.DataFrame, split_cfg: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compute annual total cases and zero-case share over the entire panel (1993-2022).
    Includes epidemic peaks, COVID-era drop, and period breakdown.
    """
    annual = (
        df.groupby("year")
        .agg(
            total_cases=("cases", "sum"),
            mean_cases=("cases", "mean"),
            zero_cases_count=("cases", lambda s: int((s == 0).sum())),
            valid_months_count=("cases", "count"),
        )
        .reset_index()
    )
    annual["zero_share_pct"] = (
        annual["zero_cases_count"] / annual["valid_months_count"]
    ) * 100.0

    annual_records = []
    for _, r in annual.iterrows():
        annual_records.append(
            {
                "year": int(r["year"]),
                "total_cases": int(r["total_cases"]),
                "mean_cases": round(float(r["mean_cases"]), 2),
                "zero_share_pct": round(float(r["zero_share_pct"]), 2),
                "valid_months": int(r["valid_months_count"]),
            }
        )

    # Epidemic peaks
    sorted_by_cases = annual.sort_values("total_cases", ascending=False)
    top_epidemic_years = sorted_by_cases.head(5)[["year", "total_cases"]].to_dict(
        orient="records"
    )
    top_epidemic_years = [
        {"year": int(x["year"]), "total_cases": int(x["total_cases"])}
        for x in top_epidemic_years
    ]

    # COVID drop
    cases_2019 = int(annual.loc[annual["year"] == 2019, "total_cases"].iloc[0])
    cases_2021 = int(annual.loc[annual["year"] == 2021, "total_cases"].iloc[0])
    zero_pct_2021 = round(
        float(annual.loc[annual["year"] == 2021, "zero_share_pct"].iloc[0]), 2
    )
    covid_drop_ratio = round(cases_2019 / max(cases_2021, 1), 2)

    # Split totals
    train_yrs = split_cfg["train_years"]
    val_yrs = split_cfg["val_years"]
    test_yrs = split_cfg["test_years"]
    norm_yrs = split_cfg["test_subperiods"]["normal"]
    cov_yrs = split_cfg["test_subperiods"]["covid"]

    def sum_period(y_start, y_end):
        sub = annual[(annual["year"] >= y_start) & (annual["year"] <= y_end)]
        return int(sub["total_cases"].sum())

    return {
        "annual_data": annual_records,
        "top_epidemic_years": top_epidemic_years,
        "peak_year": top_epidemic_years[0],
        "year_2019_cases": cases_2019,
        "year_2021_cases": cases_2021,
        "year_2021_zero_share_pct": zero_pct_2021,
        "covid_drop_ratio_2019_to_2021": covid_drop_ratio,
        "train_period_total_cases": sum_period(train_yrs[0], train_yrs[1]),
        "val_period_total_cases": sum_period(val_yrs[0], val_yrs[1]),
        "test_period_total_cases": sum_period(test_yrs[0], test_yrs[1]),
        "test_normal_cases": sum_period(norm_yrs[0], norm_yrs[1]),
        "test_covid_cases": sum_period(cov_yrs[0], cov_yrs[1]),
    }


def plot_seasonality(
    seasonality_stats: Dict[str, Any],
    out_path: str = "results/figures/eda_seasonality.png",
) -> None:
    """Generate eda_seasonality.png showing monthly dengue cases alongside rain and temp."""
    monthly_df = pd.DataFrame(seasonality_stats["monthly_profile"])
    months = monthly_df["month"]
    month_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 8), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.0]}
    )

    # Top panel: Dengue cases
    line1 = ax1.plot(
        months,
        monthly_df["mean_cases"],
        color="#1f77b4",
        marker="o",
        linewidth=2.5,
        markersize=6,
        label="Mean Cases / Province",
    )
    # Shaded SEM band
    ax1.fill_between(
        months,
        monthly_df["mean_cases"] - monthly_df["sem_cases"],
        monthly_df["mean_cases"] + monthly_df["sem_cases"],
        color="#1f77b4",
        alpha=0.2,
        label="±1 SEM",
    )
    ax1.plot(
        months,
        monthly_df["median_cases"],
        color="#08306b",
        linestyle="--",
        linewidth=1.8,
        label="Median Cases / Province",
    )

    # Annotate peak and trough
    peak_m = seasonality_stats["peak_dengue_month"]
    peak_val = seasonality_stats["peak_dengue_mean_cases"]
    trough_m = seasonality_stats["trough_dengue_month"]
    trough_val = seasonality_stats["trough_dengue_mean_cases"]

    ax1.annotate(
        f"Epidemic Peak: Jul\nMean: {peak_val:.1f} cases/prov",
        xy=(peak_m, peak_val),
        xytext=(peak_m + 0.3, peak_val + 5),
        arrowprops=dict(facecolor="#1f77b4", shrink=0.08, width=1.5, headwidth=6),
        fontsize=10,
        fontweight="bold",
        color="#08306b",
    )
    ax1.annotate(
        f"Trough: Feb\nMean: {trough_val:.1f} cases",
        xy=(trough_m, trough_val),
        xytext=(trough_m + 0.3, trough_val + 20),
        arrowprops=dict(facecolor="#555555", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9,
        color="#333333",
    )

    ax1.set_ylabel("Monthly Dengue Cases\nper Province", fontsize=11, fontweight="bold")
    ax1.set_title(
        "Monthly Seasonal Profile: Dengue Transmission vs Climate in Thailand (Train 1993–2015)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cccccc")

    # Bottom panel: Climate profile (Rainfall & Temperature)
    ax2_twin = ax2.twinx()

    # Rainfall as blue bars
    bars = ax2.bar(
        months,
        monthly_df["mean_precip_mm"],
        width=0.55,
        color="#4a90e2",
        alpha=0.6,
        edgecolor="#2a70c2",
        label="Monthly Rainfall (mm)",
    )
    # Temperature as red line with markers
    line_temp = ax2_twin.plot(
        months,
        monthly_df["mean_temp_c"],
        color="#d9534f",
        marker="s",
        linewidth=2.5,
        markersize=6,
        label="Mean Temperature (°C)",
    )

    # Annotate climate peaks
    peak_temp_m = seasonality_stats["peak_temp_month"]
    peak_temp_v = seasonality_stats["peak_temp_mean_c"]
    ax2_twin.annotate(
        f"Peak Heat: Apr ({peak_temp_v:.1f}°C)",
        xy=(peak_temp_m, peak_temp_v),
        xytext=(peak_temp_m - 2.8, peak_temp_v + 0.3),
        arrowprops=dict(facecolor="#d9534f", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="#a94442",
    )

    ax2.set_ylabel("Precipitation (mm)", fontsize=11, fontweight="bold", color="#2a70c2")
    ax2_twin.set_ylabel("Temperature (°C)", fontsize=11, fontweight="bold", color="#d9534f")
    ax2.tick_params(axis="y", labelcolor="#2a70c2")
    ax2_twin.tick_params(axis="y", labelcolor="#d9534f")
    ax2.set_xlabel("Calendar Month", fontsize=11, fontweight="bold")
    ax2.set_xticks(months)
    ax2.set_xticklabels(month_names, fontsize=10)
    ax2.grid(True, linestyle="--", alpha=0.4)

    # Combined legend for bottom panel
    handles1, labels1 = ax2.get_legend_handles_labels()
    handles2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper left",
        frameon=True,
        facecolor="white",
        edgecolor="#cccccc",
    )

    # Explanatory text box
    plt.tight_layout()
    fig.subplots_adjust(bottom=0.12)
    fig.text(
        0.5,
        0.02,
        "Epidemiological Lag Insight: Heat waves in April (28.6°C) and monsoon rains commencing in May (189.8 mm)\n"
        "fuel vector breeding (Aedes aegypti) and accelerate virus incubation, leading to epidemic peak in July (114.3 cases/prov).",
        ha="center",
        fontsize=9.5,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"),
    )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_lag_correlation(
    lag_stats: Dict[str, Any],
    out_path: str = "results/figures/eda_lag_correlation.png",
) -> None:
    """Generate eda_lag_correlation.png showing lag correlations (lags 0 to 4) on train years."""
    lags = [0, 1, 2, 3, 4]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5), sharey=True)

    colors = {
        "precip_sum_mm": "#1f77b4",
        "temp_mean_c": "#d9534f",
        "humidity_mean_pct": "#2ca02c",
    }
    labels = {
        "precip_sum_mm": "Rainfall (precip_sum_mm)",
        "temp_mean_c": "Temperature (temp_mean_c)",
        "humidity_mean_pct": "Rel. Humidity (humidity_mean_pct)",
    }
    markers = {
        "precip_sum_mm": "o",
        "temp_mean_c": "s",
        "humidity_mean_pct": "^",
    }

    # Left: Median within-province correlation with IQR error bars / ribbon
    for var, col in colors.items():
        v_data = lag_stats[var]
        medians = [d["median_within_province"] for d in v_data]
        q25 = [d["q25_within_province"] for d in v_data]
        q75 = [d["q75_within_province"] for d in v_data]

        ax1.plot(
            lags,
            medians,
            marker=markers[var],
            linewidth=2.2,
            markersize=7,
            color=col,
            label=labels[var],
        )
        ax1.fill_between(lags, q25, q75, color=col, alpha=0.15)

    ax1.axhline(0, color="gray", linestyle=":", linewidth=1.2)
    ax1.set_ylim(-0.45, 0.58)
    ax1.set_xlabel("Weather Lag (Months Prior to Transmission)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Pearson Correlation r", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Median Within-Province Correlation (n=77)", fontsize=12, fontweight="bold")
    ax1.set_xticks(lags)
    ax1.set_xticklabels([f"Lag {k}" for k in lags])
    ax1.grid(True, linestyle="--", alpha=0.4)
    ax1.legend(loc="lower left", frameon=True, fontsize=9.5)

    # Highlight peak lags on ax1
    ax1.annotate(
        "Temp peaks at\nLag 2–3 (r ≈ 0.39)",
        xy=(2.5, 0.392),
        xytext=(1.75, 0.47),
        arrowprops=dict(facecolor="#d9534f", shrink=0.08, width=1.2, headwidth=5),
        fontsize=9,
        fontweight="bold",
        color="#a94442",
    )
    ax1.annotate(
        "Rain peaks at\nLag 0–1 (r ≈ 0.28)",
        xy=(0.5, 0.257),
        xytext=(0.1, -0.15),
        arrowprops=dict(facecolor="#1f77b4", shrink=0.08, width=1.2, headwidth=5),
        fontsize=9,
        fontweight="bold",
        color="#1f77b4",
    )

    # Right: Pooled log1p correlation
    for var, col in colors.items():
        v_data = lag_stats[var]
        pooled = [d["pooled_log1p"] for d in v_data]
        ax2.plot(
            lags,
            pooled,
            marker=markers[var],
            linewidth=2.2,
            markersize=7,
            color=col,
            label=labels[var],
        )

    ax2.axhline(0, color="gray", linestyle=":", linewidth=1.2)
    ax2.set_xlabel("Weather Lag (Months Prior to Transmission)", fontsize=11, fontweight="bold")
    ax2.set_title("(b) Pooled Correlation (log1p Cases)", fontsize=12, fontweight="bold")
    ax2.set_xticks(lags)
    ax2.set_xticklabels([f"Lag {k}" for k in lags])
    ax2.grid(True, linestyle="--", alpha=0.4)
    ax2.legend(loc="lower left", frameon=True, fontsize=9.5)

    fig.suptitle(
        "Weather Lag Correlation with Dengue Cases: Train Set 1993–2015 (Strictly Leak-Free)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    fig.subplots_adjust(top=0.86, bottom=0.22)
    fig.text(
        0.5,
        0.02,
        "Empirical Feature Motivation: Temperature leads dengue outbreaks by 2–3 months (incubation & breeding);\n"
        "precipitation and humidity lead by 0–1 month. This directly justifies features weather_lags: [0, 1, 2, 3].",
        ha="center",
        fontsize=9.5,
        style="italic",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8f9fa", edgecolor="#dddddd"),
    )

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_province_heterogeneity(
    hetero_stats: Dict[str, Any],
    df: pd.DataFrame,
    out_path: str = "results/figures/eda_province_heterogeneity.png",
) -> None:
    """
    Generate eda_province_heterogeneity.png demonstrating baseline differences
    across provinces and showing why local threshold mean_p + 1*SD_p is required.
    """
    start_yr, end_yr = hetero_stats["train_years"]
    train_mask = (df["year"] >= start_yr) & (df["year"] <= end_yr)
    df_train = df[train_mask].copy()

    # Compute mean and std for all provinces
    p_summary = (
        df_train.groupby("province_en")["cases"]
        .agg(["mean", "std", "median", "max"])
        .sort_values("mean", ascending=True)
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6.5), gridspec_kw={"width_ratios": [1.1, 1.0]})

    # Left: Ranked horizontal bar chart for top 12 and bottom 12 provinces + National average
    top_10 = p_summary.tail(10)
    bottom_10 = p_summary.head(10)
    selected_p = pd.concat([bottom_10, top_10])

    y_pos = np.arange(len(selected_p))
    colors = ["#2b7bba" if m > hetero_stats["national_mean_cases"] else "#7fb3d5" for m in selected_p["mean"]]

    bars = ax1.barh(y_pos, selected_p["mean"], xerr=selected_p["std"], color=colors, alpha=0.85, capsize=3, edgecolor="#333333", linewidth=0.7)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(selected_p.index, fontsize=9.5)
    ax1.set_xlabel("Monthly Dengue Cases (Mean ± 1 SD)", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Mean Monthly Cases: Top 10 vs Bottom 10 Provinces\n(Train Period 1993–2015)", fontsize=11.5, fontweight="bold")
    ax1.axvline(hetero_stats["national_mean_cases"], color="#d9534f", linestyle="--", linewidth=1.8, label=f"National Mean ({hetero_stats['national_mean_cases']} cases)")
    ax1.grid(True, linestyle="--", alpha=0.3, axis="x")
    ax1.legend(loc="lower right", frameon=True, fontsize=9.5)

    # Annotate Bangkok disparity
    bangkok_mean = hetero_stats["highest_province"]["mean"]
    lowest_name = hetero_stats["lowest_province"]["province_en"]
    lowest_mean = hetero_stats["lowest_province"]["mean"]
    ratio = hetero_stats["ratio_top_to_bottom_mean"]

    ax1.annotate(
        f"Bangkok: {bangkok_mean:.1f} cases/mo\n({ratio:.1f}x higher than {lowest_name}: {lowest_mean:.1f})",
        xy=(bangkok_mean, len(selected_p) - 1),
        xytext=(bangkok_mean - 230, len(selected_p) - 3.5),
        arrowprops=dict(facecolor="#333333", shrink=0.08, width=1.2, headwidth=5),
        fontsize=9,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#fffde7", edgecolor="#fbc02d"),
    )

    # Right: Case distribution comparison for representative provinces illustrating threshold issue
    rep_provinces = [
        "Bangkok",
        "Chiang Mai",
        "Chonburi",
        "Khon Kaen",
        "Sing Buri",
        "Nong Bua Lamphu",
    ]
    # Filter to existing
    rep_provinces = [p for p in rep_provinces if p in df_train["province_en"].unique()]

    # Collect boxplot data
    box_data = [df_train[df_train["province_en"] == p]["cases"].dropna() for p in rep_provinces]
    bp = ax2.boxplot(
        box_data,
        tick_labels=rep_provinces,
        patch_artist=True,
        showfliers=False,  # suppress extreme outliers to keep visualization readable
        medianprops=dict(color="#111111", linewidth=1.5),
        boxprops=dict(facecolor="#d0e1fd", edgecolor="#2b7bba"),
    )

    # Plot local threshold markers (mean + 1*SD)
    for i, p in enumerate(rep_provinces):
        p_mean = df_train[df_train["province_en"] == p]["cases"].mean()
        p_std = df_train[df_train["province_en"] == p]["cases"].std()
        p_thresh = p_mean + 1.0 * p_std
        ax2.scatter(i + 1, p_thresh, color="#27ae60", marker="D", s=50, zorder=5, label="Local Threshold (mean + 1·SD)" if i == 0 else "")

    # Plot national threshold line
    nat_thresh = hetero_stats["national_threshold_mean_plus_1sd"]
    ax2.axhline(
        nat_thresh,
        color="#d9534f",
        linestyle="--",
        linewidth=2.0,
        label=f"Single National Threshold ({nat_thresh:.1f} cases)",
    )

    ax2.set_ylabel("Monthly Cases (Outlier Points Suppressed)", fontsize=11, fontweight="bold")
    ax2.set_title("(b) Per-Province Threshold vs Single National Threshold\n(Why a Single National Cutoff Fails)", fontsize=11.5, fontweight="bold")
    ax2.set_xticklabels(rep_provinces, rotation=25, ha="right", fontsize=9.5)
    ax2.grid(True, linestyle="--", alpha=0.3, axis="y")
    ax2.legend(loc="upper right", frameon=True, fontsize=9.5)

    # Text annotation on right plot
    ax2.annotate(
        f"National threshold ({nat_thresh:.0f}) exceeds the\n"
        f"historical maximum of 11 small provinces!\n"
        f"Local threshold (green diamond) scales\n"
        f"with provincial endemic baseline.",
        xy=(4.5, nat_thresh),
        xytext=(2.2, 380),
        arrowprops=dict(facecolor="#d9534f", shrink=0.08, width=1.2, headwidth=5),
        fontsize=8.5,
        fontweight="bold",
        color="#a94442",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffebee", edgecolor="#e57373"),
    )

    fig.suptitle(
        "Province Heterogeneity & Justification of Local Outbreak Thresholds (Train 1993–2015)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    plt.tight_layout()
    fig.subplots_adjust(top=0.88, bottom=0.10)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_annual_trend_covid(
    annual_stats: Dict[str, Any],
    split_cfg: Dict[str, Any],
    out_path: str = "results/figures/eda_annual_trend_covid.png",
) -> None:
    """
    Generate eda_annual_trend_covid.png showing annual total cases and zero-case share
    across 1993-2022 with train/val/test boundaries and the COVID drop.
    """
    df_annual = pd.DataFrame(annual_stats["annual_data"])
    years = df_annual["year"]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.5), sharex=True, gridspec_kw={"height_ratios": [1.2, 1.0]})

    train_end = split_cfg["train_years"][1]
    val_end = split_cfg["val_years"][1]
    test_end = split_cfg["test_years"][1]

    # Shaded split regions
    for ax in (ax1, ax2):
        ax.axvspan(1992.5, train_end + 0.5, color="#e8f4f8", alpha=0.8, zorder=0)
        ax.axvspan(train_end + 0.5, val_end + 0.5, color="#fef9e7", alpha=0.8, zorder=0)
        ax.axvspan(val_end + 0.5, test_end + 0.5, color="#eafaf1", alpha=0.8, zorder=0)
        # Vertical boundary lines
        ax.axvline(train_end + 0.5, color="#2980b9", linestyle="--", linewidth=1.5, zorder=2)
        ax.axvline(val_end + 0.5, color="#f39c12", linestyle="--", linewidth=1.5, zorder=2)
        # Divider between normal test (2018-2019) and covid test (2020-2022)
        ax.axvline(2019.5, color="#27ae60", linestyle=":", linewidth=1.5, zorder=2)

    # Top panel: Total annual cases
    ax1.plot(years, df_annual["total_cases"], color="#1a5276", marker="o", linewidth=2.4, markersize=5, zorder=3, label="Annual Total Cases")
    ax1.fill_between(years, 0, df_annual["total_cases"], color="#2980b9", alpha=0.15, zorder=2)

    # Annotate epidemic peaks
    peaks = [
        (1998, 124557),
        (2001, 104671),
        (2013, 87502),
        (2015, 86653),
        (2019, 87866),
    ]
    for yr, val in peaks:
        ax1.annotate(
            f"{yr}\n({val:,})",
            xy=(yr, val),
            xytext=(yr, val + 11000),
            ha="center",
            fontsize=8.5,
            fontweight="bold",
            color="#0b3c5d",
            arrowprops=dict(facecolor="#1a5276", shrink=0.08, width=1, headwidth=4),
        )

    # Annotate COVID drop in 2021
    cases_2021 = annual_stats["year_2021_cases"]
    ratio = annual_stats["covid_drop_ratio_2019_to_2021"]
    ax1.annotate(
        f"2021 COVID Drop\n{cases_2021:,} cases\n({ratio:.1f}x lower than 2019)",
        xy=(2021, cases_2021),
        xytext=(2021 - 3.5, cases_2021 + 35000),
        fontsize=9,
        fontweight="bold",
        color="#c0392b",
        arrowprops=dict(facecolor="#c0392b", shrink=0.08, width=1.2, headwidth=5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#ffebee", edgecolor="#ef9a9a"),
    )

    ax1.set_ylabel("Total Annual Dengue Cases", fontsize=11, fontweight="bold")
    ax1.set_title("Annual Dengue Incidence and Zero-Transmission Share (Thailand 1993–2022)", fontsize=13, fontweight="bold", pad=12)
    ax1.grid(True, linestyle="--", alpha=0.3)
    ax1.set_ylim(0, 150000)

    # Split labels on top panel
    ax1.text(2004, 138000, "TRAIN (1993–2015)", ha="center", fontsize=10, fontweight="bold", color="#1f618d")
    ax1.text(2016.5, 138000, "VAL\n(16–17)", ha="center", fontsize=8.5, fontweight="bold", color="#b7950b")
    ax1.text(2020.5, 138000, "TEST (2018–2022)\nNormal | COVID", ha="center", fontsize=8.5, fontweight="bold", color="#1e8449")

    # Bottom panel: Zero-case share
    ax2.plot(years, df_annual["zero_share_pct"], color="#c0392b", marker="s", linewidth=2.2, markersize=5, zorder=3, label="Zero-Case Province-Months (%)")
    ax2.axhline(5.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.7)

    # Annotate 2021 spike in zero cases
    zero_2021 = annual_stats["year_2021_zero_share_pct"]
    ax2.annotate(
        f"2021 Zero Surge: {zero_2021:.1f}%\n(Hospital avoidance / lockdowns)",
        xy=(2021, zero_2021),
        xytext=(2015, zero_2021 + 3),
        fontsize=9,
        fontweight="bold",
        color="#c0392b",
        arrowprops=dict(facecolor="#c0392b", shrink=0.08, width=1.2, headwidth=5),
    )

    ax2.set_xlabel("Calendar Year", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Zero-Case Province-Months (%)", fontsize=11, fontweight="bold")
    ax2.set_xticks(range(1994, 2023, 2))
    ax2.grid(True, linestyle="--", alpha=0.3)
    ax2.set_ylim(0, 30)

    plt.tight_layout()
    fig.subplots_adjust(bottom=0.10)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def run_all_eda(
    config_path: str = "config/params.yaml",
    panel_path: str = "data/processed/panel.csv",
    output_dir: str = "results",
) -> Dict[str, Any]:
    """Execute complete EDA pipeline and save all figures and stats."""
    cfg, df = load_config_and_data(config_path, panel_path)

    train_years = tuple(cfg["split"]["train_years"])
    val_years = tuple(cfg["split"]["val_years"])
    test_years = tuple(cfg["split"]["test_years"])
    split_cfg = cfg["split"]

    print(f"Loaded {len(df)} rows across {df['province_en'].nunique()} provinces.")
    print(f"Train years: {train_years}, Val years: {val_years}, Test years: {test_years}")

    # 1. Seasonality stats & figure
    print("Computing seasonality stats (train years only)...")
    seasonality_stats = compute_seasonality_stats(df, train_years)
    fig_seasonality = f"{output_dir}/figures/eda_seasonality.png"
    plot_seasonality(seasonality_stats, fig_seasonality)
    print(f"Saved: {fig_seasonality}")

    # 2. Lag correlation stats & figure
    print("Computing lag correlation stats (train years only)...")
    lag_stats = compute_lag_correlation_stats(df, train_years, max_lag=4)
    fig_lag = f"{output_dir}/figures/eda_lag_correlation.png"
    plot_lag_correlation(lag_stats, fig_lag)
    print(f"Saved: {fig_lag}")

    # 3. Province heterogeneity stats & figure
    print("Computing province heterogeneity stats (train years only)...")
    hetero_stats = compute_province_heterogeneity_stats(df, train_years)
    fig_hetero = f"{output_dir}/figures/eda_province_heterogeneity.png"
    plot_province_heterogeneity(hetero_stats, df, fig_hetero)
    print(f"Saved: {fig_hetero}")

    # 4. Annual trend & COVID stats & figure
    print("Computing annual trends and COVID drop stats (1993-2022)...")
    annual_stats = compute_annual_trend_stats(df, split_cfg)
    fig_annual = f"{output_dir}/figures/eda_annual_trend_covid.png"
    plot_annual_trend_covid(annual_stats, split_cfg, fig_annual)
    print(f"Saved: {fig_annual}")

    # Compile comprehensive stats dictionary
    all_stats = {
        "split_definitions": {
            "train_years": list(train_years),
            "val_years": list(val_years),
            "test_years": list(test_years),
            "test_subperiods": split_cfg["test_subperiods"],
        },
        "panel_overview": {
            "total_rows": len(df),
            "provinces_count": int(df["province_en"].nunique()),
            "years_span": [int(df["year"].min()), int(df["year"].max())],
            "train_rows": int(((df["year"] >= train_years[0]) & (df["year"] <= train_years[1])).sum()),
            "train_valid_case_rows": int(
                df[(df["year"] >= train_years[0]) & (df["year"] <= train_years[1])]["cases"]
                .notna()
                .sum()
            ),
            "train_missing_case_rows": int(
                df[(df["year"] >= train_years[0]) & (df["year"] <= train_years[1])]["cases"]
                .isna()
                .sum()
            ),
        },
        "seasonality": seasonality_stats,
        "lag_correlations": lag_stats,
        "province_heterogeneity": hetero_stats,
        "annual_trends": annual_stats,
    }

    stats_path = Path(output_dir) / "eda_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, indent=2)
    print(f"Saved numerical statistics to: {stats_path}")

    return all_stats


if __name__ == "__main__":
    run_all_eda()
