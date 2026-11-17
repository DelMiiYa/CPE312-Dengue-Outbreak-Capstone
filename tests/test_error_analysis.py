"""Unit tests for Quantitative Error Analysis (T08, Poster Box R5)."""

import json
from pathlib import Path
from PIL import Image
import pytest


@pytest.fixture(scope="module")
def error_analysis_data():
    """Load results/error_analysis.json."""
    json_path = Path("results/error_analysis.json")
    assert json_path.exists(), "results/error_analysis.json does not exist. Run error_analysis.py first."
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_error_analysis_json_schema(error_analysis_data):
    """Verify top-level keys and dataset summary in error_analysis.json."""
    expected_top_keys = {
        "dataset_summary",
        "onset_vs_ongoing",
        "fp_anatomy_hgb",
        "geographic_burden_tiers",
        "temporal_breakdown",
        "case_studies",
    }
    assert expected_top_keys.issubset(set(error_analysis_data.keys()))

    ds = error_analysis_data["dataset_summary"]
    assert ds["total_test_rows"] == 4620
    assert ds["total_outbreaks"] == 392
    assert ds["total_non_outbreaks"] == 4228
    assert ds["test_years"] == [2018, 2022]
    assert 0.0 < ds["hgb_operating_threshold"] < 1.0


def test_onset_vs_ongoing_conservation(error_analysis_data):
    """Verify arithmetic conservation for onset vs ongoing outbreaks."""
    onset_data = error_analysis_data["onset_vs_ongoing"]
    breakdown = onset_data["breakdown"]

    assert breakdown["total_outbreaks"] == 392
    assert breakdown["onset_count"] == 148
    assert breakdown["ongoing_count"] == 244
    assert breakdown["onset_count"] + breakdown["ongoing_count"] == 392

    # Verify all models preserve row counts
    for model_key in [
        "persistence_last_month",
        "logistic_regression",
        "random_forest",
        "hist_gradient_boosting",
    ]:
        m = onset_data[model_key]
        assert m["onset"]["total"] == 148
        assert m["ongoing"]["total"] == 244
        assert m["overall"]["total"] == 392

        assert m["onset"]["tp"] + m["onset"]["fn"] == 148
        assert m["ongoing"]["tp"] + m["ongoing"]["fn"] == 244
        assert m["overall"]["tp"] + m["overall"]["fn"] == 392

    # Specific locked properties
    # 1. Persistence has 0% recall on onsets
    assert onset_data["persistence_last_month"]["onset"]["tp"] == 0
    assert onset_data["persistence_last_month"]["onset"]["recall"] == 0.0
    assert onset_data["persistence_last_month"]["ongoing"]["recall"] == 1.0

    # 2. HistGradientBoosting breakdown
    hgb = onset_data["hist_gradient_boosting"]
    assert hgb["onset"]["tp"] == 108
    assert hgb["onset"]["fn"] == 40
    assert hgb["ongoing"]["tp"] == 238
    assert hgb["ongoing"]["fn"] == 6
    assert hgb["overall"]["tp"] == 346
    assert hgb["overall"]["fn"] == 46

    # 3. False Negative Share
    fn_share = hgb["fn_share"]
    assert fn_share["total_fn"] == 46
    assert fn_share["onset_fn"] == 40
    assert fn_share["ongoing_fn"] == 6
    assert abs(fn_share["onset_fn_pct"] - 40 / 46 * 100) < 1e-4

    # 4. Dynamics: missed onsets have larger case jump than detected
    dynamics = hgb["onset_case_dynamics"]
    assert dynamics["missed_mean_case_jump"] > dynamics["detected_mean_case_jump"]
    assert dynamics["missed_mean_prior_zscore"] < dynamics["detected_mean_prior_zscore"]


def test_fp_anatomy_conservation(error_analysis_data):
    """Verify FP breakdown arithmetic conservation and properties."""
    fp_data = error_analysis_data["fp_anatomy_hgb"]
    assert fp_data["total_fp"] == 295

    # Mutually exclusive partition sum
    me = fp_data["mutually_exclusive_partition"]
    me_sum = (
        me["elevated_endemic_near_miss"]["count"]
        + me["post_outbreak_tail"]["count"]
        + me["pre_outbreak_early_warning"]["count"]
        + me["pure_false_alarm"]["count"]
    )
    assert me_sum == 295

    assert me["post_outbreak_tail"]["count"] == 109
    assert me["elevated_endemic_near_miss"]["count"] == 121
    assert me["pre_outbreak_early_warning"]["count"] == 46
    assert me["pure_false_alarm"]["count"] == 19

    # Benign / actionable union
    assert fp_data["at_least_one_benign"]["count"] == 276
    assert fp_data["pure_false_alarm"]["count"] == 19
    assert fp_data["at_least_one_benign"]["count"] + fp_data["pure_false_alarm"]["count"] == 295

    # Over 90% are near-miss or post-tail or early warning
    assert fp_data["at_least_one_benign"]["pct"] > 90.0

    # Near-miss raw count
    assert fp_data["elevated_endemic_near_miss"]["count"] == 268

    # Ratios
    assert fp_data["mean_ratio_target_to_threshold_fp"] > 0.60
    assert fp_data["mean_ratio_target_to_threshold_tn"] < 0.25


def test_geographic_burden_tiers_conservation(error_analysis_data):
    """Verify province burden tier classification and confusion matrix conservation."""
    geo = error_analysis_data["geographic_burden_tiers"]
    defs = geo["tier_definitions"]

    # 77 provinces partitioned into tertiles
    assert defs["Low"]["provinces_count"] == 26
    assert defs["Medium"]["provinces_count"] == 25
    assert defs["High"]["provinces_count"] == 26
    assert defs["Low"]["provinces_count"] + defs["Medium"]["provinces_count"] + defs["High"]["provinces_count"] == 77

    # Metrics conservation
    tiers = geo["metrics_by_tier"]
    total_rows = sum(tiers[t]["rows"] for t in ["Low", "Medium", "High"])
    total_pos = sum(tiers[t]["pos"] for t in ["Low", "Medium", "High"])
    total_tp = sum(tiers[t]["tp"] for t in ["Low", "Medium", "High"])
    total_fp = sum(tiers[t]["fp"] for t in ["Low", "Medium", "High"])
    total_fn = sum(tiers[t]["fn"] for t in ["Low", "Medium", "High"])
    total_tn = sum(tiers[t]["tn"] for t in ["Low", "Medium", "High"])

    assert total_rows == 4620
    assert total_pos == 392
    assert total_tp == 346
    assert total_fp == 295
    assert total_fn == 46
    assert total_tn == 3933

    for t in ["Low", "Medium", "High"]:
        assert tiers[t]["tp"] + tiers[t]["fn"] == tiers[t]["pos"]
        assert tiers[t]["fp"] + tiers[t]["tn"] == tiers[t]["rows"] - tiers[t]["pos"]


def test_temporal_breakdown_conservation(error_analysis_data):
    """Verify annual, subperiod, and monthly temporal breakdowns conserve exactly."""
    temp = error_analysis_data["temporal_breakdown"]

    # By year
    by_yr = temp["by_year"]
    assert set(by_yr.keys()) == {"2018", "2019", "2020", "2021", "2022"}
    assert sum(by_yr[y]["rows"] for y in by_yr) == 4620
    assert sum(by_yr[y]["pos"] for y in by_yr) == 392
    assert sum(by_yr[y]["tp"] for y in by_yr) == 346
    assert sum(by_yr[y]["fp"] for y in by_yr) == 295
    assert sum(by_yr[y]["fn"] for y in by_yr) == 46
    assert sum(by_yr[y]["tn"] for y in by_yr) == 3933

    # By subperiod
    by_sp = temp["by_subperiod"]
    assert set(by_sp.keys()) == {"normal_2018_2019", "covid_2020_2022"}
    assert sum(by_sp[s]["rows"] for s in by_sp) == 4620
    assert sum(by_sp[s]["pos"] for s in by_sp) == 392
    assert sum(by_sp[s]["tp"] for s in by_sp) == 346
    assert sum(by_sp[s]["fp"] for s in by_sp) == 295
    assert sum(by_sp[s]["fn"] for s in by_sp) == 46
    assert sum(by_sp[s]["tn"] for s in by_sp) == 3933

    # By month (1..12)
    by_mo = temp["by_target_month"]
    assert len(by_mo) == 12
    assert sum(by_mo[m]["rows"] for m in by_mo) == 4620
    assert sum(by_mo[m]["pos"] for m in by_mo) == 392
    assert sum(by_mo[m]["tp"] for m in by_mo) == 346
    assert sum(by_mo[m]["fp"] for m in by_mo) == 295
    assert sum(by_mo[m]["fn"] for m in by_mo) == 46
    assert sum(by_mo[m]["tn"] for m in by_mo) == 3933


def test_case_studies_integrity(error_analysis_data):
    """Verify that case studies are non-empty, well-formed, and follow label semantics."""
    cs = error_analysis_data["case_studies"]
    assert len(cs["false_negatives"]) == 3
    assert len(cs["false_positives"]) == 3
    assert len(cs["early_onset_true_positives"]) == 3

    for fn_case in cs["false_negatives"]:
        assert fn_case["outbreak_t1"] == 1
        assert fn_case["pred_hist_gradient_boosting"] == 0
        assert len(fn_case["explanation"]) > 10

    for fp_case in cs["false_positives"]:
        assert fp_case["outbreak_t1"] == 0
        assert fp_case["pred_hist_gradient_boosting"] == 1
        assert len(fp_case["explanation"]) > 10

    for tp_case in cs["early_onset_true_positives"]:
        assert tp_case["outbreak_t1"] == 1
        assert tp_case["outbreak_lag_0"] == 0
        assert tp_case["pred_persistence_last_month"] == 0
        assert tp_case["pred_hist_gradient_boosting"] == 1
        assert len(tp_case["explanation"]) > 10


def test_figure_file():
    """Verify that r5_error_analysis.png exists, is valid, > 20 KB, and has 300 DPI."""
    fig_path = Path("results/figures/r5_error_analysis.png")
    assert fig_path.exists(), "results/figures/r5_error_analysis.png does not exist"
    assert fig_path.stat().st_size > 20 * 1024, f"Figure too small: {fig_path.stat().st_size} bytes"

    with Image.open(fig_path) as img:
        assert img.format == "PNG"
        dpi = img.info.get("dpi", (0, 0))
        assert dpi[0] >= 295, f"Expected ~300 DPI, got {dpi}"


def test_markdown_report_concordance():
    """Verify that results/error_analysis.md exists and contains verified numbers."""
    md_path = Path("results/error_analysis.md")
    assert md_path.exists(), "results/error_analysis.md does not exist"
    content = md_path.read_text(encoding="utf-8")

    # Key statistics check
    assert "73.0%" in content
    assert "0.0%" in content
    assert "93.6%" in content
    assert "88.3%" in content
    assert "40 / 46" in content or "40/46" in content
    assert "Bueng Kan" in content
    assert "Samut Sakhon" in content
    assert "Chaiyaphum" in content
    assert "Nakhon Phanom" in content
    assert "Chiang Rai" in content
