"""Automated tests enforcing zero data leakage, strict time splits, and feature correctness."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.features.build_features import (
    build_modeling_table,
    compute_province_thresholds,
    load_params,
)


@pytest.fixture(scope="module")
def params():
    """Load default config params."""
    return load_params("config/params.yaml")


@pytest.fixture(scope="module")
def panel():
    """Load processed panel data."""
    path = Path("data/processed/panel.csv")
    assert path.exists(), "data/processed/panel.csv must exist before running feature tests"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def thresholds(panel, params):
    """Compute province thresholds."""
    return compute_province_thresholds(panel, params)


@pytest.fixture(scope="module")
def modeling_data(panel, thresholds, params):
    """Build clean modeling table, dropped rows, and feature column list."""
    return build_modeling_table(panel, thresholds, params)


def test_train_only_thresholds(panel, thresholds, params):
    """Modifying cases in validation/test years (>= 2016) must not change thresholds at all."""
    mutated_panel = panel.copy()

    # Mutate post-2015 cases drastically
    val_test_mask = mutated_panel["year"] >= 2016
    mutated_panel.loc[val_test_mask, "cases"] = 999999.0

    mutated_thresholds = compute_province_thresholds(mutated_panel, params)

    # Must be bitwise identical
    pd.testing.assert_frame_equal(mutated_thresholds, thresholds)

    # Sanity check: mutating a train year (<= 2015) MUST alter thresholds
    train_mutated = panel.copy()
    train_mask = (train_mutated["year"] == 2010) & (train_mutated["province_en"] == "Bangkok")
    train_mutated.loc[train_mask, "cases"] = 999999.0
    train_thresholds = compute_province_thresholds(train_mutated, params)

    bkk_orig = thresholds.loc[thresholds["province_en"] == "Bangkok", "threshold_p"].iloc[0]
    bkk_mut = train_thresholds.loc[train_thresholds["province_en"] == "Bangkok", "threshold_p"].iloc[0]
    assert bkk_orig != bkk_mut, "Mutating train cases should alter Bangkok's threshold"


def test_strict_temporal_causality(panel, thresholds, params):
    """Modifying cases or weather at month t+1 must not change any feature column at row t."""
    clean_orig, _, feature_cols = build_modeling_table(panel, thresholds, params)

    # Test perturbation across multiple provinces and points in time
    test_cases = [
        ("Bangkok", 2015, 6),       # Train set
        ("Chiang Mai", 2016, 8),    # Val set
        ("Phuket", 2019, 4),        # Test set normal
        ("Khon Kaen", 2021, 5),     # Test set covid
    ]

    for prov, t_year, t_month in test_cases:
        # Determine t+1 calendar date
        t1_year = t_year + 1 if t_month == 12 else t_year
        t1_month = 1 if t_month == 12 else t_month + 1

        mutated_panel = panel.copy()
        target_mask = (
            (mutated_panel["province_en"] == prov)
            & (mutated_panel["year"] == t1_year)
            & (mutated_panel["month"] == t1_month)
        )
        assert target_mask.sum() == 1, f"Expected 1 matching row for {prov} at {t1_year}-{t1_month}"

        # Drastically perturb cases and weather at month t+1
        mutated_panel.loc[target_mask, "cases"] = 88888.0
        mutated_panel.loc[target_mask, "temp_mean_c"] = 99.0
        mutated_panel.loc[target_mask, "precip_sum_mm"] = 9999.0
        mutated_panel.loc[target_mask, "humidity_mean_pct"] = 1.0

        clean_mut, _, _ = build_modeling_table(mutated_panel, thresholds, params)

        # Features at month t (and all months <= t) must remain strictly identical
        orig_prov_up_to_t = clean_orig[
            (clean_orig["province_en"] == prov)
            & (
                (clean_orig["year"] < t_year)
                | ((clean_orig["year"] == t_year) & (clean_orig["month"] <= t_month))
            )
        ]
        mut_prov_up_to_t = clean_mut[
            (clean_mut["province_en"] == prov)
            & (
                (clean_mut["year"] < t_year)
                | ((clean_mut["year"] == t_year) & (clean_mut["month"] <= t_month))
            )
        ]

        pd.testing.assert_frame_equal(
            orig_prov_up_to_t[feature_cols].reset_index(drop=True),
            mut_prov_up_to_t[feature_cols].reset_index(drop=True),
        )

        # Target at month t should change because month t+1 cases changed
        orig_row_t = clean_orig[
            (clean_orig["province_en"] == prov)
            & (clean_orig["year"] == t_year)
            & (clean_orig["month"] == t_month)
        ]
        mut_row_t = clean_mut[
            (clean_mut["province_en"] == prov)
            & (clean_mut["year"] == t_year)
            & (clean_mut["month"] == t_month)
        ]
        assert orig_row_t["target_cases_t1"].iloc[0] != mut_row_t["target_cases_t1"].iloc[0]
        assert mut_row_t["target_cases_t1"].iloc[0] == 88888.0


def test_no_nan_and_split_completeness():
    """Val (1,848 rows) and test (4,620 rows) cover all 77 provinces with 0 NaNs."""
    thresh_path = Path("data/processed/province_thresholds.csv")
    model_path = Path("data/processed/modeling_table.csv")

    assert thresh_path.exists(), f"File missing: {thresh_path}"
    assert model_path.exists(), f"File missing: {model_path}"

    t_df = pd.read_csv(thresh_path)
    m_df = pd.read_csv(model_path)

    # Threshold checks
    assert t_df.shape == (77, 5)
    assert t_df.isna().sum().sum() == 0
    assert set(t_df.columns) == {"province_en", "train_months", "mean_p", "sd_p", "threshold_p"}
    assert (t_df["threshold_p"] > t_df["mean_p"]).all()
    assert (t_df["train_months"] == 276).sum() == 72
    assert (t_df["train_months"] == 156).sum() == 4
    assert (t_df["train_months"] == 60).sum() == 1

    # Modeling table checks
    assert m_df.isna().sum().sum() == 0
    assert len(m_df) == 26100

    # Target integrity
    assert set(m_df["outbreak_t1"].unique()).issubset({0, 1})

    # Split completeness
    split_counts = m_df.groupby("split").agg(
        rows=("outbreak_t1", "size"),
        provs=("province_en", "nunique"),
        min_ty=("target_year", "min"),
        max_ty=("target_year", "max"),
    )

    # Validation: 77 provinces * 24 months (2016-2017) = 1,848 rows
    assert split_counts.loc["val", "rows"] == 1848
    assert split_counts.loc["val", "provs"] == 77
    assert split_counts.loc["val", "min_ty"] == 2016
    assert split_counts.loc["val", "max_ty"] == 2017

    # Test: 77 provinces * 60 months (2018-2022) = 4,620 rows
    assert split_counts.loc["test", "rows"] == 4620
    assert split_counts.loc["test", "provs"] == 77
    assert split_counts.loc["test", "min_ty"] == 2018
    assert split_counts.loc["test", "max_ty"] == 2022

    # Train: 77 provinces, 1994-2015 = 19,632 rows
    assert split_counts.loc["train", "rows"] == 19632
    assert split_counts.loc["train", "provs"] == 77
    assert split_counts.loc["train", "min_ty"] == 1994
    assert split_counts.loc["train", "max_ty"] == 2015

    # Test subperiods
    test_normal = m_df[(m_df["split"] == "test") & (m_df["subperiod"] == "normal")]
    test_covid = m_df[(m_df["split"] == "test") & (m_df["subperiod"] == "covid")]
    assert len(test_normal) == 1848
    assert len(test_covid) == 2772


def test_feature_engineering_exact_math(panel, modeling_data):
    """Verify specific mathematical calculations of lags, rolling means, and baseline helpers."""
    clean_df, _, _ = modeling_data

    # Check a specific row: Bangkok at 2016-05
    sample_row = clean_df[
        (clean_df["province_en"] == "Bangkok")
        & (clean_df["year"] == 2016)
        & (clean_df["month"] == 5)
    ].iloc[0]

    bkk_panel = panel[panel["province_en"] == "Bangkok"].set_index(["year", "month"])

    c_m0 = bkk_panel.loc[(2016, 5), "cases"]
    c_m1 = bkk_panel.loc[(2016, 4), "cases"]
    c_m2 = bkk_panel.loc[(2016, 3), "cases"]
    c_m3 = bkk_panel.loc[(2016, 2), "cases"]
    c_target = bkk_panel.loc[(2016, 6), "cases"]
    c_last_year = bkk_panel.loc[(2015, 6), "cases"]

    assert sample_row["cases_lag_0"] == pytest.approx(c_m0)
    assert sample_row["cases_lag_1"] == pytest.approx(c_m1)
    assert sample_row["cases_lag_2"] == pytest.approx(c_m2)
    assert sample_row["cases_lag_3"] == pytest.approx(c_m3)
    assert sample_row["cases_roll_mean_3"] == pytest.approx((c_m0 + c_m1 + c_m2) / 3.0)
    assert sample_row["target_cases_t1"] == pytest.approx(c_target)

    thresh = sample_row["threshold_p"]
    assert sample_row["outbreak_lag_0"] == int(c_m0 > thresh)
    assert sample_row["outbreak_same_month_last_year"] == int(c_last_year > thresh)
    assert sample_row["outbreak_t1"] == int(c_target > thresh)

    expected_z = (c_m0 - sample_row["mean_p"]) / sample_row["sd_p"]
    assert sample_row["cases_zscore_lag_0"] == pytest.approx(expected_z)


def test_feature_summary_json():
    """Verify results/feature_summary.json exists and accurately mirrors the dataset."""
    summary_path = Path("results/feature_summary.json")
    assert summary_path.exists(), "results/feature_summary.json must exist"

    with open(summary_path, "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["total_panel_rows"] == 27720
    assert summary["modeling_table_rows"] == 26100
    assert summary["total_dropped_rows"] == 1620

    accounting = summary["dropped_rows_accounting"]["breakdown"]
    sum_breakdown = sum(item["count"] for item in accounting.values())
    assert sum_breakdown == 1620

    splits = summary["splits"]
    assert splits["train"]["rows"] == 19632
    assert splits["val"]["rows"] == 1848
    assert splits["test"]["rows"] == 4620
    assert splits["test_normal_2018_2019"]["rows"] == 1848
    assert splits["test_covid_2020_2022"]["rows"] == 2772
