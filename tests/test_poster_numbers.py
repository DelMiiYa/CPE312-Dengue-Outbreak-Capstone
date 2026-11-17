"""
Pytest suite verifying numerical consistency and structure of poster content and summary.
Audits:
  - poster/poster_R1_to_R7_th.md
  - _agent/docs/SUMMARY_TH.md
  - poster/qr_colab.png
  - poster/qr_opendengue.png
  - poster/qr_weather.png
Against:
  - results/metrics.json
  - results/eda_stats.json
  - results/feature_summary.json
  - results/error_analysis.json
  - results/policy_analysis.json
"""

import json
from pathlib import Path
import cv2
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def results_data():
    """Load all quantitative JSON artifacts."""
    results_dir = REPO_ROOT / "results"
    with open(results_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(results_dir / "eda_stats.json", "r", encoding="utf-8") as f:
        eda = json.load(f)
    with open(results_dir / "feature_summary.json", "r", encoding="utf-8") as f:
        feat = json.load(f)
    with open(results_dir / "error_analysis.json", "r", encoding="utf-8") as f:
        err = json.load(f)
    with open(results_dir / "policy_analysis.json", "r", encoding="utf-8") as f:
        pol = json.load(f)

    return {
        "metrics": metrics,
        "eda": eda,
        "feat": feat,
        "err": err,
        "pol": pol,
    }


@pytest.fixture(scope="module")
def poster_text():
    """Load poster markdown text."""
    poster_path = REPO_ROOT / "poster" / "poster_R1_to_R7_th.md"
    assert poster_path.exists(), f"Missing file: {poster_path}"
    with open(poster_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def summary_text():
    """Load Thai summary markdown text."""
    summary_path = REPO_ROOT / "_agent" / "docs" / "SUMMARY_TH.md"
    assert summary_path.exists(), f"Missing file: {summary_path}"
    with open(summary_path, "r", encoding="utf-8") as f:
        return f.read()


def test_required_files_exist_and_non_empty():
    """Verify that all output files exist with substantial content."""
    poster_md = REPO_ROOT / "poster" / "poster_R1_to_R7_th.md"
    summary_md = REPO_ROOT / "_agent" / "docs" / "SUMMARY_TH.md"
    qr_colab = REPO_ROOT / "poster" / "qr_colab.png"
    qr_dengue = REPO_ROOT / "poster" / "qr_opendengue.png"
    qr_weather = REPO_ROOT / "poster" / "qr_weather.png"

    assert poster_md.exists() and poster_md.stat().st_size > 10000
    assert summary_md.exists() and summary_md.stat().st_size > 3000
    assert qr_colab.exists() and qr_colab.stat().st_size > 500
    assert qr_dengue.exists() and qr_dengue.stat().st_size > 500
    assert qr_weather.exists() and qr_weather.stat().st_size > 500


def test_zero_tbd_or_unverified_placeholders(poster_text, summary_text):
    """Ensure zero occurrences of TBD or UNVERIFIED placeholders."""
    for name, text in [("poster", poster_text), ("summary", summary_text)]:
        assert "TBD" not in text, f"Found TBD placeholder in {name}"
        assert "UNVERIFIED" not in text, f"Found UNVERIFIED placeholder in {name}"


def test_poster_box_structure(poster_text):
    """Verify presence of all mandatory poster boxes (Header, R1-R7, Footer, Blueprint)."""
    mandatory_sections = [
        "Poster Header",
        "Box R1",
        "Box R2",
        "Box R3",
        "Box R4",
        "Box R5",
        "Box R6",
        "Box R7",
        "Footer & QR Codes",
        "Visual Layout Blueprint",
    ]
    for sec in mandatory_sections:
        assert sec in poster_text, f"Missing section '{sec}' in poster/poster_R1_to_R7_th.md"


def test_qr_codes_scannability():
    """Validate that all 3 generated QR code PNGs decode accurately via OpenCV."""
    detector = cv2.QRCodeDetector()
    expected = {
        "qr_colab.png": "https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS",
        "qr_opendengue.png": "https://opendengue.org",
        "qr_weather.png": "https://open-meteo.com/en/docs/historical-weather-api",
    }
    for fname, exp_url in expected.items():
        img_path = REPO_ROOT / "poster" / fname
        img = cv2.imread(str(img_path))
        assert img is not None, f"Failed to load image: {img_path}"
        decoded_text, _, _ = detector.detectAndDecode(img)
        assert decoded_text == exp_url, f"QR decode mismatch for {fname}: got '{decoded_text}', expected '{exp_url}'"


def test_model_metrics_numbers_consistency(poster_text, summary_text, results_data):
    """Verify that model metrics numbers in poster and summary match metrics.json exactly."""
    m = results_data["metrics"]
    hgb_test = m["models"]["hist_gradient_boosting"]["metrics"]["test"]
    pers_test = m["baselines"]["persistence_last_month"]["test"]
    thresh = m["models"]["hist_gradient_boosting"]["threshold_used"]

    hgb_rec_str = f"{hgb_test['recall']*100:.2f}%"
    pers_rec_str = f"{pers_test['recall']*100:.2f}%"
    diff_str = f"{(hgb_test['recall'] - pers_test['recall'])*100:.2f}"
    thresh_str = f"{thresh:.2f}"
    lr_thresh_str = f"{m['models']['logistic_regression']['threshold_used']:.2f}"
    rf_thresh_str = f"{m['models']['random_forest']['threshold_used']:.2f}"
    fn_reduction_str = f"{(pers_test['fn'] - hgb_test['fn'])/pers_test['fn']*100:.1f}%"

    assert hgb_rec_str in poster_text  # 88.27%
    assert pers_rec_str in poster_text  # 62.24%
    assert diff_str in poster_text  # 26.02
    assert thresh_str in poster_text  # 0.49
    assert lr_thresh_str in poster_text  # 0.54
    assert rf_thresh_str in poster_text  # 0.45
    assert fn_reduction_str in poster_text  # 68.9%

    assert hgb_rec_str in summary_text
    assert pers_rec_str in summary_text


def test_eda_findings_numbers_consistency(poster_text, summary_text, results_data):
    """Verify that EDA numbers in poster and summary match eda_stats.json."""
    eda = results_data["eda"]
    peak_temp_c = f"{eda['seasonality']['peak_temp_mean_c']:.2f}°C"  # 28.60°C
    peak_dengue = f"{eda['seasonality']['peak_dengue_mean_cases']:.2f}"  # 114.31
    monsoon_rain = f"{eda['seasonality']['monsoon_onset_mean_precip_mm']:.2f} mm"  # 189.84 mm
    temp_corr = f"{eda['lag_correlations']['temp_mean_c'][3]['median_within_province']:.4f}"  # 0.3940
    rain_corr = f"{eda['lag_correlations']['precip_sum_mm'][0]['median_within_province']:.4f}"  # 0.2853

    het_ratio = f"{eda['province_heterogeneity']['ratio_top_to_bottom_mean']:.2f}"  # 49.78
    bkk_mean = f"{eda['province_heterogeneity']['highest_province']['mean']:.2f}"  # 354.45
    nongbua_mean = f"{eda['province_heterogeneity']['lowest_province']['mean']:.2f}"  # 7.12
    masked_count = str(eda["province_heterogeneity"]["provinces_never_reaching_national_threshold_count"])  # 11

    drop_ratio = f"{eda['annual_trends']['covid_drop_ratio_2019_to_2021']:.2f}"  # 11.30
    cases_2019 = f"{eda['annual_trends']['year_2019_cases']:,}"  # 87,866
    cases_2021 = f"{eda['annual_trends']['year_2021_cases']:,}"  # 7,778

    for s in [
        peak_temp_c,
        peak_dengue,
        monsoon_rain,
        temp_corr,
        rain_corr,
        het_ratio,
        bkk_mean,
        nongbua_mean,
        masked_count,
        drop_ratio,
        cases_2019,
        cases_2021,
    ]:
        assert s in poster_text, f"Missing EDA value '{s}' in poster"
        assert s in summary_text, f"Missing EDA value '{s}' in summary"


def test_data_splits_consistency(poster_text, summary_text, results_data):
    """Verify dataset dimensions and split sizes match feature_summary.json."""
    feat = results_data["feat"]
    total_panel = f"{feat['total_panel_rows']:,}"  # 27,720
    total_model = f"{feat['modeling_table_rows']:,}"  # 26,100
    train_rows = f"{feat['splits']['train']['rows']:,}"  # 19,632
    val_rows = f"{feat['splits']['val']['rows']:,}"  # 1,848
    test_rows = f"{feat['splits']['test']['rows']:,}"  # 4,620
    outbreaks = str(feat["splits"]["test"]["outbreak_count"])  # 392

    for s in [total_panel, total_model, train_rows, val_rows, test_rows, outbreaks]:
        assert s in poster_text, f"Missing split value '{s}' in poster"
        assert s in summary_text, f"Missing split value '{s}' in summary"


def test_error_analysis_numbers_consistency(poster_text, summary_text, results_data):
    """Verify error breakdown metrics match error_analysis.json."""
    err = results_data["err"]
    onset_cnt = str(err["onset_vs_ongoing"]["breakdown"]["onset_count"])  # 148
    ongoing_cnt = str(err["onset_vs_ongoing"]["breakdown"]["ongoing_count"])  # 244
    pers_onset_rec = f"{err['onset_vs_ongoing']['persistence_last_month']['onset']['recall']*100:.1f}%"  # 0.0%
    hgb_onset_rec = f"{err['onset_vs_ongoing']['hist_gradient_boosting']['onset']['recall']*100:.1f}%"  # 73.0%
    fn_onset_pct = f"{err['onset_vs_ongoing']['hist_gradient_boosting']['fn_share']['onset_fn_pct']:.1f}%"  # 87.0%
    case_jump = f"{err['onset_vs_ongoing']['hist_gradient_boosting']['onset_case_dynamics']['missed_mean_case_jump']:.2f}"  # 3.35

    fp_actionable = f"{err['fp_anatomy_hgb']['at_least_one_benign']['pct']:.1f}%"  # 93.6%
    fp_pure = f"{err['fp_anatomy_hgb']['pure_false_alarm']['pct']:.1f}%"  # 6.4%
    fp_nearmiss = f"{err['fp_anatomy_hgb']['mutually_exclusive_partition']['elevated_endemic_near_miss']['pct']:.1f}%"  # 41.0%
    fp_tail = f"{err['fp_anatomy_hgb']['mutually_exclusive_partition']['post_outbreak_tail']['pct']:.1f}%"  # 36.9%
    fp_early = f"{err['fp_anatomy_hgb']['mutually_exclusive_partition']['pre_outbreak_early_warning']['pct']:.1f}%"  # 15.6%

    for s in [
        onset_cnt,
        ongoing_cnt,
        pers_onset_rec,
        hgb_onset_rec,
        fn_onset_pct,
        case_jump,
        fp_actionable,
        fp_pure,
        fp_nearmiss,
        fp_tail,
        fp_early,
    ]:
        assert s in poster_text, f"Missing error analysis value '{s}' in poster"


def test_policy_and_two_tier_consistency(poster_text, summary_text, results_data):
    """Verify policy and Two-Tier numbers match policy_analysis.json."""
    pol = results_data["pol"]
    green_pct = f"{pol['two_tier_test']['green']['pct_months']:.1f}%"  # 83.8%
    green_risk = f"{pol['two_tier_test']['green']['outbreak_rate']*100:.2f}%"  # 0.90%
    yellow_pct = f"{pol['two_tier_test']['yellow']['pct_months']:.1f}%"  # 4.8%
    yellow_risk = f"{pol['two_tier_test']['yellow']['outbreak_rate']*100:.2f}%"  # 17.12%
    red_pct = f"{pol['two_tier_test']['red']['pct_months']:.1f}%"  # 11.4%
    red_risk = f"{pol['two_tier_test']['red']['outbreak_rate']*100:.2f}%"  # 60.53%
    comb_rec = f"{pol['two_tier_test']['overall_alert_zone']['recall']*100:.2f}%"  # 91.07%

    for s in [green_pct, green_risk, yellow_pct, yellow_risk, red_pct, red_risk, comb_rec]:
        assert s in poster_text, f"Missing policy value '{s}' in poster"
        assert s in summary_text, f"Missing policy value '{s}' in summary"

    # Cost savings & reductions
    assert "65.9%" in poster_text
    assert "69.7%" in poster_text
    assert "72.2%" in poster_text
    assert "85.0%" in poster_text
    assert "56.0%" in poster_text
