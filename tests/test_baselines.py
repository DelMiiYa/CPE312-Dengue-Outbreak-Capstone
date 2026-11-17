"""Unit tests for baseline classifiers and evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.models.baselines import (
    compute_metrics,
    evaluate_baselines,
    get_splits,
    load_params,
    update_metrics_json,
)


@pytest.fixture(scope="module")
def modeling_df() -> pd.DataFrame:
    """Load modeling table DataFrame."""
    path = Path("data/processed/modeling_table.csv")
    assert path.exists(), f"Modeling table not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def metrics_json_data() -> dict:
    """Load results/metrics.json."""
    path = Path("results/metrics.json")
    assert path.exists(), f"results/metrics.json not found at {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_get_splits_sizes_and_ranges(modeling_df: pd.DataFrame) -> None:
    """Verify all 5 evaluation splits have exact required row counts and year ranges."""
    splits = get_splits(modeling_df)

    expected_splits = {
        "train": (19632, 1994, 2015),
        "val": (1848, 2016, 2017),
        "test": (4620, 2018, 2022),
        "test_normal_2018_2019": (1848, 2018, 2019),
        "test_covid_2020_2022": (2772, 2020, 2022),
    }

    for split_name, (exp_rows, exp_min_yr, exp_max_yr) in expected_splits.items():
        assert split_name in splits, f"Missing split: {split_name}"
        sdf = splits[split_name]
        assert len(sdf) == exp_rows, f"Split {split_name} row count {len(sdf)} != {exp_rows}"
        assert sdf["target_year"].min() == exp_min_yr, (
            f"Split {split_name} min year {sdf['target_year'].min()} != {exp_min_yr}"
        )
        assert sdf["target_year"].max() == exp_max_yr, (
            f"Split {split_name} max year {sdf['target_year'].max()} != {exp_max_yr}"
        )


def test_compute_metrics_basic_cases() -> None:
    """Verify compute_metrics on synthetic known confusion matrices."""
    # Perfect predictions
    y_true = np.array([0, 0, 1, 1])
    y_pred = np.array([0, 0, 1, 1])
    m_perfect = compute_metrics(y_true, y_pred)
    assert m_perfect["recall"] == 1.0
    assert m_perfect["precision"] == 1.0
    assert m_perfect["f1"] == 1.0
    assert m_perfect["specificity"] == 1.0
    assert m_perfect["accuracy"] == 1.0
    assert m_perfect["tp"] == 2
    assert m_perfect["tn"] == 2
    assert m_perfect["fp"] == 0
    assert m_perfect["fn"] == 0
    assert m_perfect["support_pos"] == 2
    assert m_perfect["support_total"] == 4

    # All zeros (majority class behavior)
    y_pred_zero = np.array([0, 0, 0, 0])
    m_zero = compute_metrics(y_true, y_pred_zero, y_score=np.full(4, 0.5))
    assert m_zero["recall"] == 0.0
    assert m_zero["precision"] == 0.0
    assert m_zero["f1"] == 0.0
    assert m_zero["specificity"] == 1.0
    assert m_zero["accuracy"] == 0.5
    assert m_zero["tp"] == 0
    assert m_zero["fn"] == 2


def test_majority_class_behavior(modeling_df: pd.DataFrame) -> None:
    """Verify majority class predicts 0 with 0.0 recall across all splits."""
    results = evaluate_baselines(modeling_df)
    maj = results["majority_class"]

    for split_name, m in maj.items():
        assert m["recall"] == 0.0
        assert m["precision"] == 0.0
        assert m["f1"] == 0.0
        assert m["tp"] == 0
        assert m["fp"] == 0
        assert m["fn"] == m["support_pos"]
        assert m["specificity"] == 1.0
        assert np.isclose(m["accuracy"], m["tn"] / m["support_total"])
        # Constant score pr_auc equals positive prevalence in that split
        pos_prev = m["support_pos"] / m["support_total"]
        assert np.isclose(m["pr_auc"], pos_prev)


def test_persistence_logic(modeling_df: pd.DataFrame) -> None:
    """Verify persistence matches outbreak_lag_0 predictions and reports continuous z-score PR-AUC."""
    results = evaluate_baselines(modeling_df)
    pers = results["persistence_last_month"]
    splits = get_splits(modeling_df)

    for split_name, m in pers.items():
        sdf = splits[split_name]
        y_true = sdf["outbreak_t1"].values
        y_pred = sdf["outbreak_lag_0"].values

        # Confusion matrix checks
        expected_tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        expected_fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        expected_tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        expected_fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        assert m["tp"] == expected_tp
        assert m["fp"] == expected_fp
        assert m["tn"] == expected_tn
        assert m["fn"] == expected_fn

        # Auxiliary continuous score should be stored
        assert "pr_auc_continuous_zscore" in m
        assert 0.0 <= m["pr_auc_continuous_zscore"] <= 1.0
        # Continuous z-score PR-AUC should exceed binary flag PR-AUC on test set
        if split_name in ["test", "test_normal_2018_2019", "test_covid_2020_2022"]:
            assert m["pr_auc_continuous_zscore"] > m["pr_auc"]


def test_seasonal_logic(modeling_df: pd.DataFrame) -> None:
    """Verify seasonal baseline matches outbreak_same_month_last_year predictions."""
    results = evaluate_baselines(modeling_df)
    seas = results["seasonal_last_year"]
    splits = get_splits(modeling_df)

    for split_name, m in seas.items():
        sdf = splits[split_name]
        y_true = sdf["outbreak_t1"].values
        y_pred = sdf["outbreak_same_month_last_year"].values

        expected_tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        expected_fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        expected_tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        expected_fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        assert m["tp"] == expected_tp
        assert m["fp"] == expected_fp
        assert m["tn"] == expected_tn
        assert m["fn"] == expected_fn


def test_confusion_matrix_identities(modeling_df: pd.DataFrame) -> None:
    """Verify algebraic and boundary identities for all baseline metrics."""
    results = evaluate_baselines(modeling_df)

    for b_name, splits_dict in results.items():
        for s_name, m in splits_dict.items():
            # Identity: total count
            assert m["tp"] + m["fp"] + m["tn"] + m["fn"] == m["support_total"]
            # Identity: positive count
            assert m["tp"] + m["fn"] == m["support_pos"]
            # Identity: negative count
            assert m["tn"] + m["fp"] == m["support_total"] - m["support_pos"]

            # Boundary checks
            for metric_key in ["recall", "precision", "f1", "pr_auc", "specificity", "accuracy"]:
                assert 0.0 <= m[metric_key] <= 1.0, f"{b_name} {s_name} {metric_key} out of range"

            # Accuracy identity
            expected_acc = (m["tp"] + m["tn"]) / m["support_total"]
            assert np.isclose(m["accuracy"], expected_acc)


def test_metrics_json_structure(metrics_json_data: dict) -> None:
    """Verify results/metrics.json preserves 'dataset' and properly formats 'baselines'."""
    assert "dataset" in metrics_json_data, "Existing 'dataset' key was lost"
    assert "baselines" in metrics_json_data, "Missing 'baselines' key"

    expected_baselines = ["majority_class", "persistence_last_month", "seasonal_last_year"]
    expected_splits = ["train", "val", "test", "test_normal_2018_2019", "test_covid_2020_2022"]
    required_metrics = [
        "recall",
        "precision",
        "f1",
        "pr_auc",
        "specificity",
        "accuracy",
        "tp",
        "fp",
        "tn",
        "fn",
        "support_pos",
        "support_total",
    ]

    for b in expected_baselines:
        assert b in metrics_json_data["baselines"], f"Missing baseline {b}"
        for s in expected_splits:
            assert s in metrics_json_data["baselines"][b], f"Missing split {s} in baseline {b}"
            entry = metrics_json_data["baselines"][b][s]
            for metric in required_metrics:
                assert metric in entry, f"Missing metric {metric} in baselines[{b}][{s}]"


def test_report_numbers_match_json(metrics_json_data: dict) -> None:
    """Verify that results/baselines_report.md exists and matches results/metrics.json numbers."""
    report_path = Path("results/baselines_report.md")
    assert report_path.exists(), "results/baselines_report.md does not exist"
    report_text = report_path.read_text(encoding="utf-8")

    baselines = metrics_json_data["baselines"]
    eval_splits = ["val", "test", "test_normal_2018_2019", "test_covid_2020_2022"]

    for b_key in baselines:
        for s_key in eval_splits:
            m = baselines[b_key][s_key]
            # Formatted strings that should exist in the report table
            recall_str = f"{m['recall']:.4f}"
            prec_str = f"{m['precision']:.4f}"
            f1_str = f"{m['f1']:.4f}"
            pr_auc_str = f"{m['pr_auc']:.4f}"
            tp_str = f"{m['tp']}"
            fp_str = f"{m['fp']}"
            fn_str = f"{m['fn']}"

            assert recall_str in report_text, f"Recall {recall_str} for {b_key} {s_key} not in report"
            assert prec_str in report_text, f"Precision {prec_str} for {b_key} {s_key} not in report"
            assert f1_str in report_text, f"F1 {f1_str} for {b_key} {s_key} not in report"
            assert pr_auc_str in report_text, f"PR-AUC {pr_auc_str} for {b_key} {s_key} not in report"
            assert tp_str in report_text, f"TP {tp_str} for {b_key} {s_key} not in report"
            assert fp_str in report_text, f"FP {fp_str} for {b_key} {s_key} not in report"
            assert fn_str in report_text, f"FN {fn_str} for {b_key} {s_key} not in report"
