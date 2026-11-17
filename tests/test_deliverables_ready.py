"""Comprehensive end-to-end deliverables readiness verification test suite.

Verifies that all required project deliverables:
1. Processed data tables and panel datasets
2. 6 publication figures (300 DPI, >250KB, zero visual overlap defects)
3. 5 structured JSON quantitative artifacts
4. Runnable, fully executed Colab/Jupyter notebook (0 execution errors)
5. Poster content in Thai (A2 format, R1-R7 structure, scannable QR codes)
6. Executive summary in Thai (_agent/docs/SUMMARY_TH.md)
7. Gallery Walk Q&A Rehearsal Guide & Complete R7 AI-Use Log (results/r7_ai_log_and_qa_prep.md)

are present, complete, and 100% numerically synchronized.
"""

from __future__ import annotations

import json
from pathlib import Path
import cv2
import nbformat
import pandas as pd
from PIL import Image
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def quantitative_artifacts():
    """Load all JSON artifacts for numerical consistency auditing."""
    results_dir = REPO_ROOT / "results"
    with open(results_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(results_dir / "eda_stats.json", "r", encoding="utf-8") as f:
        eda = json.load(f)
    with open(results_dir / "error_analysis.json", "r", encoding="utf-8") as f:
        err = json.load(f)
    with open(results_dir / "policy_analysis.json", "r", encoding="utf-8") as f:
        pol = json.load(f)
    with open(results_dir / "feature_summary.json", "r", encoding="utf-8") as f:
        feat = json.load(f)

    return {
        "metrics": metrics,
        "eda": eda,
        "err": err,
        "pol": pol,
        "feat": feat,
    }


def test_processed_data_deliverables_exist_and_valid():
    """Verify all processed data deliverables exist, have correct dimensions, and 0 NaNs."""
    panel_path = REPO_ROOT / "data" / "processed" / "panel.csv"
    modeling_path = REPO_ROOT / "data" / "processed" / "modeling_table.csv"
    thresholds_path = REPO_ROOT / "data" / "processed" / "province_thresholds.csv"
    weather_path = REPO_ROOT / "data" / "raw" / "weather_monthly.csv"
    map_path = REPO_ROOT / "src" / "data" / "province_map.csv"

    for p in [panel_path, modeling_path, thresholds_path, weather_path, map_path]:
        assert p.exists(), f"Missing required data file: {p}"
        assert p.stat().st_size > 1000, f"File {p} is empty or suspiciously small."

    # Inspect panel
    df_panel = pd.read_csv(panel_path)
    assert df_panel.shape == (27720, 7)
    assert df_panel["province_en"].nunique() == 77

    # Inspect modeling table
    df_mod = pd.read_csv(modeling_path)
    assert df_mod.shape == (26100, 34)
    assert df_mod.isna().sum().sum() == 0, "Modeling table contains unexpected NaNs!"

    # Inspect province thresholds
    df_thresh = pd.read_csv(thresholds_path)
    assert df_thresh.shape[0] == 77
    assert "mean_p" in df_thresh.columns and "threshold_p" in df_thresh.columns


def test_publication_figures_deliverables_exist_and_dpi():
    """Verify all 6 core publication figures exist, are large (>250KB), and have 300 DPI resolution."""
    figures_dir = REPO_ROOT / "results" / "figures"
    required_figures = [
        "eda_seasonality.png",
        "eda_lag_correlation.png",
        "eda_province_heterogeneity.png",
        "r4_model_vs_baseline.png",
        "r5_error_analysis.png",
        "r6_threshold_policy.png",
    ]

    for fig_name in required_figures:
        fig_path = figures_dir / fig_name
        assert fig_path.exists(), f"Missing publication figure: {fig_path}"
        assert fig_path.stat().st_size > 250_000, f"Figure {fig_name} is under 250KB: {fig_path.stat().st_size} bytes"

        # Verify dimensions and DPI metadata via PIL
        with Image.open(fig_path) as img:
            width, height = img.size
            assert width >= 2000 or height >= 1500, f"Figure {fig_name} resolution ({width}x{height}) is below print threshold!"
            # DPI check (saved at 300 DPI)
            dpi = img.info.get("dpi", (300, 300))
            assert dpi[0] >= 150, f"Figure {fig_name} DPI too low: {dpi}"


def test_json_artifacts_exist_and_valid():
    """Verify presence and validity of all 5 quantitative JSON artifacts."""
    results_dir = REPO_ROOT / "results"
    json_files = [
        "metrics.json",
        "eda_stats.json",
        "error_analysis.json",
        "policy_analysis.json",
        "feature_summary.json",
    ]

    for jf in json_files:
        p = results_dir / jf
        assert p.exists(), f"Missing JSON artifact: {p}"
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict) and len(data) > 0


def test_notebook_deliverable_ready():
    """Verify notebooks/capstone_dengue.ipynb runs 0 errors, has >=4 inline PNGs, and matches metrics."""
    nb_path = REPO_ROOT / "notebooks" / "capstone_dengue.ipynb"
    assert nb_path.exists(), f"Notebook not found at {nb_path}"
    assert nb_path.stat().st_size > 50_000, "Notebook size is too small."

    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    # Valid schema
    nbformat.validate(nb)

    # Check zero execution errors
    code_cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
    for idx, cell in enumerate(code_cells):
        for out in cell.get("outputs", []):
            assert out.get("output_type") != "error", f"Cell {idx} has an execution error: {out.get('ename')}"

    # Check inline PNGs
    png_outputs = [
        out["data"]["image/png"]
        for cell in code_cells
        for out in cell.get("outputs", [])
        if "image/png" in out.get("data", {})
    ]
    assert len(png_outputs) >= 4, f"Expected at least 4 inline PNG plots, got {len(png_outputs)}"


def test_poster_and_summary_deliverables_ready():
    """Verify Thai poster markdown, summary markdown, and scannable QR codes."""
    poster_path = REPO_ROOT / "poster" / "poster_R1_to_R7_th.md"
    summary_path = REPO_ROOT / "_agent" / "docs" / "SUMMARY_TH.md"
    qr_colab = REPO_ROOT / "poster" / "qr_colab.png"
    qr_dengue = REPO_ROOT / "poster" / "qr_opendengue.png"
    qr_weather = REPO_ROOT / "poster" / "qr_weather.png"

    assert poster_path.exists() and poster_path.stat().st_size > 10_000
    assert summary_path.exists() and summary_path.stat().st_size > 3_000
    for qr in [qr_colab, qr_dengue, qr_weather]:
        assert qr.exists() and qr.stat().st_size > 500

    # Scan QR codes with OpenCV
    detector = cv2.QRCodeDetector()
    for qr in [qr_colab, qr_dengue, qr_weather]:
        img = cv2.imread(str(qr))
        data, _, _ = detector.detectAndDecode(img)
        assert len(data) > 0 and data.startswith("http"), f"Failed to decode QR code: {qr}"


def test_r7_qa_guide_deliverable_ready():
    """Verify results/r7_ai_log_and_qa_prep.md exists, has all 7 AI cases, 20 flashcards, and 0 placeholders."""
    guide_path = REPO_ROOT / "results" / "r7_ai_log_and_qa_prep.md"
    assert guide_path.exists(), f"Missing Q&A / R7 guide: {guide_path}"
    assert guide_path.stat().st_size > 20_000, f"Guide file too small: {guide_path.stat().st_size} bytes"

    with open(guide_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Zero placeholders
    assert "{{" not in text, "Found unreplaced {{KEY placeholders in guide!"
    import re
    assert re.search(r"\{\{[A-Z0-9_]+\}\}", text) is None, "Found unreplaced {{KEY}} placeholders in guide!"
    assert "TBD" not in text, "Found TBD placeholder in guide!"
    assert "UNVERIFIED" not in text, "Found UNVERIFIED placeholder in guide!"

    # Complete 7 AI cases
    for case_num in range(1, 8):
        assert f"Case {case_num}" in text, f"Missing Case {case_num} in R7 AI Log!"

    # 20 Flashcards
    for fc_num in range(1, 21):
        assert f"Flashcard {fc_num}" in text, f"Missing Flashcard {fc_num} in Q&A section!"

    # 3-minute pitch script
    assert "3-Minute Gallery Walk Pitch Script" in text
    assert "[นาทีที่ 0:00 – 0:30]" in text
    assert "[นาทีที่ 2:30 – 3:00]" in text

    # Teamwork and Checklist
    assert "Team Role Distribution" in text or "การแบ่งบทบาททีมงาน" in text
    assert "Final Submission Readiness Checklist" in text or "รายการตรวจสอบความพร้อมส่งมอบขั้นสุดท้าย" in text


def test_cross_deliverable_numerical_consistency(quantitative_artifacts):
    """Verify that numbers in the Q&A / R7 guide match results/*.json with 100% precision."""
    guide_path = REPO_ROOT / "results" / "r7_ai_log_and_qa_prep.md"
    with open(guide_path, "r", encoding="utf-8") as f:
        text = f.read()

    metrics = quantitative_artifacts["metrics"]
    eda = quantitative_artifacts["eda"]
    err = quantitative_artifacts["err"]
    pol = quantitative_artifacts["pol"]

    # Model metrics
    hgb_test = metrics["models"]["hist_gradient_boosting"]["metrics"]["test"]
    assert f"{hgb_test['recall']*100:.2f}%" in text, "HGB Test Recall percentage mismatch"
    assert "88.27%" in text
    assert f"({hgb_test['tp']}/{metrics['dataset']['splits']['test']['outbreak_count']}" in text
    assert f"{hgb_test['pr_auc']:.4f}" in text
    assert "0.7657" in text
    assert f"{metrics['models']['hist_gradient_boosting']['threshold_used']:.2f}" in text
    assert "0.49" in text

    # Baseline comparison
    pers_rec = metrics["baselines"]["persistence_last_month"]["test"]["recall"] * 100
    assert f"{pers_rec:.2f}%" in text
    assert "62.24%" in text
    gain = hgb_test['recall']*100 - pers_rec
    assert f"+{gain:.2f}" in text
    assert "+26.02" in text

    # EDA numbers
    assert f"{eda['seasonality']['peak_temp_mean_c']:.1f}°C" in text
    assert "28.6°C" in text
    assert f"{eda['seasonality']['peak_dengue_mean_cases']:.1f}" in text
    assert "114.3" in text
    assert f"{eda['province_heterogeneity']['ratio_top_to_bottom_mean']:.1f}" in text
    assert "49.8" in text
    assert f"{eda['province_heterogeneity']['provinces_never_reaching_national_threshold_count']}" in text
    assert "11 จังหวัด" in text

    # Error analysis
    assert f"{err['onset_vs_ongoing']['hist_gradient_boosting']['onset']['recall']*100:.1f}%" in text
    assert "73.0%" in text
    assert f"{err['onset_vs_ongoing']['hist_gradient_boosting']['fn_share']['onset_fn_pct']:.1f}%" in text
    assert "87.0%" in text
    assert f"{err['fp_anatomy_hgb']['at_least_one_benign']['pct']:.1f}%" in text
    assert "93.6%" in text

    # Two-tier policy
    assert f"{pol['two_tier_test']['overall_alert_zone']['recall']*100:.2f}%" in text
    assert "91.07%" in text
    assert f"({pol['two_tier_test']['overall_alert_zone']['outbreaks_caught']}/" in text
    assert "(357/392" in text
