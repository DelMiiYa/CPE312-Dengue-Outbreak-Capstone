"""
Unit tests for Exploratory Data Analysis (EDA) artifacts and stats.
Verifies file existence, sizes, JSON schema, and strict train-years computation
(anti-leakage rule).
"""

from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
import yaml

from src.eda.run_eda import (
    load_config_and_data,
    compute_lag_correlation_stats,
    compute_seasonality_stats,
    compute_province_heterogeneity_stats,
)


@pytest.fixture(scope="module")
def paths_and_data():
    config_path = "config/params.yaml"
    panel_path = "data/processed/panel.csv"
    stats_path = "results/eda_stats.json"

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    with open(stats_path, "r", encoding="utf-8") as f:
        stats = json.load(f)

    df = pd.read_csv(panel_path)
    df = df.sort_values(["province_en", "year", "month"]).reset_index(drop=True)

    return {
        "cfg": cfg,
        "stats": stats,
        "df": df,
    }


def test_figures_exist_and_non_empty():
    """All 4 EDA figures must exist in results/figures/ and exceed 20 KB each."""
    fig_dir = Path("results/figures")
    required_figures = [
        "eda_seasonality.png",
        "eda_lag_correlation.png",
        "eda_province_heterogeneity.png",
        "eda_annual_trend_covid.png",
    ]

    for fig_name in required_figures:
        fig_path = fig_dir / fig_name
        assert fig_path.exists(), f"Figure missing: {fig_path}"
        size_bytes = fig_path.stat().st_size
        assert (
            size_bytes > 20_000
        ), f"Figure {fig_name} is too small ({size_bytes} bytes <= 20 KB)"


def test_eda_stats_json_valid_and_structured(paths_and_data):
    """eda_stats.json must contain all required top-level sections matching config."""
    stats = paths_and_data["stats"]
    cfg = paths_and_data["cfg"]

    required_keys = [
        "split_definitions",
        "panel_overview",
        "seasonality",
        "lag_correlations",
        "province_heterogeneity",
        "annual_trends",
    ]
    for k in required_keys:
        assert k in stats, f"Missing top-level key: {k}"

    # Check split definitions match config/params.yaml
    assert stats["split_definitions"]["train_years"] == cfg["split"]["train_years"]
    assert stats["split_definitions"]["val_years"] == cfg["split"]["val_years"]
    assert stats["split_definitions"]["test_years"] == cfg["split"]["test_years"]
    assert (
        stats["split_definitions"]["test_subperiods"]
        == cfg["split"]["test_subperiods"]
    )


def test_lag_correlations_computed_strictly_on_train_years(paths_and_data):
    """
    Verify that lag correlations in eda_stats.json are computed strictly on train years (1993-2015).
    Re-running computation on train years must match eda_stats.json exactly.
    """
    stats = paths_and_data["stats"]
    cfg = paths_and_data["cfg"]
    df = paths_and_data["df"]

    train_years = tuple(cfg["split"]["train_years"])
    recomputed_train = compute_lag_correlation_stats(df, train_years, max_lag=4)

    for var in ["precip_sum_mm", "temp_mean_c", "humidity_mean_pct"]:
        expected_list = stats["lag_correlations"][var]
        recomputed_list = recomputed_train[var]
        assert len(expected_list) == len(recomputed_list) == 5

        for k in range(5):
            exp = expected_list[k]
            rec = recomputed_list[k]
            assert exp["lag"] == rec["lag"] == k
            assert exp["median_within_province"] == pytest.approx(
                rec["median_within_province"], abs=1e-4
            )
            assert exp["pooled_log1p"] == pytest.approx(
                rec["pooled_log1p"], abs=1e-4
            )

    # Prove anti-leakage: computing across all years (1993-2022) yields different numbers
    all_years = (int(df["year"].min()), int(df["year"].max()))
    recomputed_all = compute_lag_correlation_stats(df, all_years, max_lag=4)
    train_temp_lag2 = stats["lag_correlations"]["temp_mean_c"][2]["median_within_province"]
    all_temp_lag2 = recomputed_all["temp_mean_c"][2]["median_within_province"]
    # They should not be identical, proving post-train data alters statistics
    assert train_temp_lag2 != all_temp_lag2


def test_province_heterogeneity_train_years_strictly(paths_and_data):
    """Verify province heterogeneity is computed strictly on train years."""
    stats = paths_and_data["stats"]
    cfg = paths_and_data["cfg"]
    df = paths_and_data["df"]

    train_years = tuple(cfg["split"]["train_years"])
    recomputed = compute_province_heterogeneity_stats(df, train_years)

    assert stats["province_heterogeneity"]["national_mean_cases"] == pytest.approx(
        recomputed["national_mean_cases"], abs=1e-2
    )
    assert stats["province_heterogeneity"]["highest_province"]["mean"] == pytest.approx(
        recomputed["highest_province"]["mean"], abs=1e-2
    )
    assert stats["province_heterogeneity"]["lowest_province"]["mean"] == pytest.approx(
        recomputed["lowest_province"]["mean"], abs=1e-2
    )
    assert stats["province_heterogeneity"]["provinces_never_reaching_national_threshold_count"] == 11


def test_seasonality_peak_months_train_years(paths_and_data):
    """Verify seasonality peak months in train years."""
    stats = paths_and_data["stats"]
    cfg = paths_and_data["cfg"]
    df = paths_and_data["df"]

    train_years = tuple(cfg["split"]["train_years"])
    recomputed = compute_seasonality_stats(df, train_years)

    assert stats["seasonality"]["peak_dengue_month"] == 7  # July
    assert stats["seasonality"]["trough_dengue_month"] == 2  # February
    assert stats["seasonality"]["peak_temp_month"] == 4  # April
    assert stats["seasonality"]["peak_precip_month"] == 9  # September
    assert stats["seasonality"]["peak_dengue_mean_cases"] == pytest.approx(
        recomputed["peak_dengue_mean_cases"], abs=1e-2
    )
