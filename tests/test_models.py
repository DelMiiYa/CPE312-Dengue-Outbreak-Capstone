"""Unit tests for ML models, validation tuning, and evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.models.train_models import FEATURE_COLS, ID_COLS, TARGET_COLS


@pytest.fixture(scope="module")
def metrics_json_data() -> dict:
    """Load results/metrics.json."""
    path = Path("results/metrics.json")
    assert path.exists(), f"results/metrics.json not found at {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def val_predictions() -> pd.DataFrame:
    """Load data/processed/val_predictions.csv."""
    path = Path("data/processed/val_predictions.csv")
    assert path.exists(), f"val_predictions.csv not found at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def test_predictions() -> pd.DataFrame:
    """Load data/processed/test_predictions.csv."""
    path = Path("data/processed/test_predictions.csv")
    assert path.exists(), f"test_predictions.csv not found at {path}"
    return pd.read_csv(path)


def test_models_keys_in_metrics_json(metrics_json_data: dict) -> None:
    """Verify metrics.json contains required model metadata and preserves dataset/baselines."""
    assert "dataset" in metrics_json_data, "Missing 'dataset' key in metrics.json"
    assert "baselines" in metrics_json_data, "Missing 'baselines' key in metrics.json"
    assert "models" in metrics_json_data, "Missing 'models' key in metrics.json"
    assert "best_model_name" in metrics_json_data, "Missing 'best_model_name' key in metrics.json"
    assert "features_used" in metrics_json_data, "Missing 'features_used' key in metrics.json"

    expected_models = {"logistic_regression", "random_forest", "hist_gradient_boosting"}
    assert set(metrics_json_data["models"].keys()) == expected_models

    assert metrics_json_data["best_model_name"] in expected_models
    assert len(metrics_json_data["features_used"]) == 25


def test_feature_matrix_anti_leakage(metrics_json_data: dict) -> None:
    """Verify feature set excludes target, future, and identification columns."""
    forbidden = {"target_cases_t1", "outbreak_t1", "target_year", "year", "split", "subperiod"}
    features = set(metrics_json_data["features_used"])
    overlap = forbidden.intersection(features)
    assert not overlap, f"Forbidden leakage columns found in features: {overlap}"
    assert features == set(FEATURE_COLS)


def test_model_metrics_schema_and_integrity(metrics_json_data: dict) -> None:
    """Verify metric schema, numerical bounds, and confusion matrix arithmetic across all splits."""
    models = metrics_json_data["models"]
    expected_splits = ["train", "val", "test", "test_normal_2018_2019", "test_covid_2020_2022"]
    expected_metric_keys = {
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
    }

    expected_support = {
        "train": (1923, 19632),
        "val": (70, 1848),
        "test": (392, 4620),
        "test_normal_2018_2019": (269, 1848),
        "test_covid_2020_2022": (123, 2772),
    }

    for model_name, m_info in models.items():
        assert "best_params" in m_info, f"Missing best_params for {model_name}"
        assert "threshold_used" in m_info, f"Missing threshold_used for {model_name}"
        assert 0.0 < m_info["threshold_used"] < 1.0, f"Invalid threshold for {model_name}"
        assert "threshold_tuning_rule" in m_info, f"Missing threshold_tuning_rule for {model_name}"
        assert "feature_importances" in m_info, f"Missing feature_importances for {model_name}"
        assert len(m_info["feature_importances"]) == 25, f"Expected 25 feature importances for {model_name}"

        metrics_by_split = m_info["metrics"]
        for split_name in expected_splits:
            assert split_name in metrics_by_split, f"Missing split '{split_name}' for model '{model_name}'"
            m = metrics_by_split[split_name]
            assert set(m.keys()) == expected_metric_keys, f"Incomplete metrics schema for {model_name} on {split_name}"

            # Probability and rate metrics in [0, 1]
            for rate_key in ["recall", "precision", "f1", "pr_auc", "specificity", "accuracy"]:
                assert 0.0 <= m[rate_key] <= 1.0, f"{rate_key} out of bounds: {m[rate_key]}"

            # Confusion matrix integer arithmetic
            tp, fp, tn, fn = m["tp"], m["fp"], m["tn"], m["fn"]
            support_pos, support_total = m["support_pos"], m["support_total"]

            exp_pos, exp_tot = expected_support[split_name]
            assert support_pos == exp_pos, f"support_pos {support_pos} != {exp_pos} on {split_name}"
            assert support_total == exp_tot, f"support_total {support_total} != {exp_tot} on {split_name}"

            assert tp + fn == support_pos, f"TP ({tp}) + FN ({fn}) != support_pos ({support_pos})"
            assert tp + fp + tn + fn == support_total, f"CM sum != support_total ({support_total})"
            assert m["accuracy"] == pytest.approx((tp + tn) / support_total, abs=1e-4)


def test_models_substantially_beat_baselines_on_test(metrics_json_data: dict) -> None:
    """Verify ML models achieve substantially higher recall and PR-AUC than baselines on test set."""
    baselines = metrics_json_data["baselines"]
    models = metrics_json_data["models"]

    pers_recall = baselines["persistence_last_month"]["test"]["recall"]
    pers_f1 = baselines["persistence_last_month"]["test"]["f1"]
    seas_recall = baselines["seasonal_last_year"]["test"]["recall"]

    for m_name in ["logistic_regression", "random_forest", "hist_gradient_boosting"]:
        m_test = models[m_name]["metrics"]["test"]

        # All ML models must beat persistence baseline recall (0.6224) by > 15 percentage points
        assert m_test["recall"] > pers_recall + 0.15, (
            f"Model {m_name} recall ({m_test['recall']:.4f}) did not beat persistence ({pers_recall:.4f})"
        )

        # All ML models must beat seasonal baseline recall (0.2832)
        assert m_test["recall"] > seas_recall + 0.40

        # All ML models must maintain F1 > persistence baseline F1
        assert m_test["f1"] > pers_f1, f"Model {m_name} F1 ({m_test['f1']:.4f}) <= persistence F1 ({pers_f1:.4f})"

        # Precision must not collapse (< 0.40 would indicate indiscriminate alarming)
        assert m_test["precision"] >= 0.50, f"Model {m_name} precision collapsed: {m_test['precision']:.4f}"

        # PR-AUC must beat persistence binary PR-AUC
        assert m_test["pr_auc"] > baselines["persistence_last_month"]["test"]["pr_auc"]


def test_val_predictions_integrity(val_predictions: pd.DataFrame, metrics_json_data: dict) -> None:
    """Verify val_predictions.csv has exact row count, zero NaNs, and valid probabilities/predictions."""
    assert len(val_predictions) == 1848, f"val_predictions row count {len(val_predictions)} != 1848"
    assert val_predictions.isna().sum().sum() == 0, "val_predictions contains NaNs"

    required_cols = [
        *ID_COLS,
        *TARGET_COLS,
        "pred_majority_class",
        "pred_persistence_last_month",
        "pred_seasonal_last_year",
        "prob_logistic_regression",
        "pred_logistic_regression",
        "prob_random_forest",
        "pred_random_forest",
        "prob_hist_gradient_boosting",
        "pred_hist_gradient_boosting",
    ]
    for col in required_cols:
        assert col in val_predictions.columns, f"Missing column '{col}' in val_predictions.csv"

    # Probabilities in [0, 1], predictions in {0, 1}
    for m_name in ["logistic_regression", "random_forest", "hist_gradient_boosting"]:
        probs = val_predictions[f"prob_{m_name}"]
        preds = val_predictions[f"pred_{m_name}"]
        thr = metrics_json_data["models"][m_name]["threshold_used"]

        assert probs.between(0.0, 1.0).all()
        assert set(preds.unique()).issubset({0, 1})

        # Verify thresholding consistency
        expected_preds = (probs >= thr).astype(int)
        assert (preds == expected_preds).all(), f"Prediction mismatch with threshold {thr} for {m_name}"


def test_test_predictions_integrity(test_predictions: pd.DataFrame, metrics_json_data: dict) -> None:
    """Verify test_predictions.csv has exact row count, zero NaNs, and valid probabilities/predictions."""
    assert len(test_predictions) == 4620, f"test_predictions row count {len(test_predictions)} != 4620"
    assert test_predictions.isna().sum().sum() == 0, "test_predictions contains NaNs"

    required_cols = [
        *ID_COLS,
        *TARGET_COLS,
        "pred_majority_class",
        "pred_persistence_last_month",
        "pred_seasonal_last_year",
        "prob_logistic_regression",
        "pred_logistic_regression",
        "prob_random_forest",
        "pred_random_forest",
        "prob_hist_gradient_boosting",
        "pred_hist_gradient_boosting",
    ]
    for col in required_cols:
        assert col in test_predictions.columns, f"Missing column '{col}' in test_predictions.csv"

    for m_name in ["logistic_regression", "random_forest", "hist_gradient_boosting"]:
        probs = test_predictions[f"prob_{m_name}"]
        preds = test_predictions[f"pred_{m_name}"]
        thr = metrics_json_data["models"][m_name]["threshold_used"]

        assert probs.between(0.0, 1.0).all()
        assert set(preds.unique()).issubset({0, 1})

        expected_preds = (probs >= thr).astype(int)
        assert (preds == expected_preds).all(), f"Prediction mismatch with threshold {thr} for {m_name}"


def test_r4_figure_and_report_files_exist() -> None:
    """Verify generated figure and report exist and satisfy requirements."""
    fig_path = Path("results/figures/r4_model_vs_baseline.png")
    assert fig_path.exists(), "r4_model_vs_baseline.png not found"
    assert fig_path.stat().st_size > 20 * 1024, "Figure size <= 20 KB"

    report_path = Path("results/modeling_report.md")
    assert report_path.exists(), "modeling_report.md not found"
    content = report_path.read_text(encoding="utf-8")
    assert "HistGradientBoosting" in content
    assert "Logistic Regression" in content
    assert "Random Forest" in content
    assert "COVID-19" in content
