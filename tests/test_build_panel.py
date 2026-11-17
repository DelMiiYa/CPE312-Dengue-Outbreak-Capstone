"""Tests for building clean panel and data mapping."""

from pathlib import Path
import pandas as pd
import pytest
from src.data.build_panel import build_panel, load_province_map


def test_province_map_structure_and_coverage():
    """Verify that province_map.csv covers all 78 OpenDengue names and 77 centroid provinces."""
    map_path = Path("src/data/province_map.csv")
    centroid_path = Path("src/data/province_centroids.csv")

    assert map_path.exists(), "src/data/province_map.csv must exist"
    assert centroid_path.exists(), "src/data/province_centroids.csv must exist"

    df_map = pd.read_csv(map_path)
    df_centroids = pd.read_csv(centroid_path)

    # 78 OpenDengue names mapping to 77 official provinces
    assert len(df_map) == 78
    assert df_map["adm_1_name_opendengue"].nunique() == 78
    assert df_map["province_en"].nunique() == 77
    assert df_map.isna().sum().sum() == 0

    # Ensure all centroid provinces are covered in mapping
    expected_provinces = set(df_centroids["province_en"])
    mapped_provinces = set(df_map["province_en"])
    assert mapped_provinces == expected_provinces

    # Verify that Prachin Buri is the only province mapped from 2 names
    counts = df_map["province_en"].value_counts()
    assert counts["Prachin Buri"] == 2
    assert (counts == 1).sum() == 76


def test_build_panel_merge_logic():
    """Verify build_panel merge logic preserves weather grid and creates NA cases for missing records."""
    weather_df = pd.DataFrame({
        "province_en": ["Chiang Mai", "Chiang Mai", "Bueng Kan", "Bueng Kan"],
        "year": [2010, 2010, 2010, 2010],
        "month": [1, 2, 1, 2],
        "temp_mean_c": [22.0, 23.0, 24.0, 25.0],
        "precip_sum_mm": [10.0, 15.0, 5.0, 0.0],
        "humidity_mean_pct": [65.0, 70.0, 60.0, 55.0],
    })

    # Bueng Kan has no cases in 2010 (starts in 2011)
    dengue_df = pd.DataFrame({
        "province_en": ["Chiang Mai", "Chiang Mai"],
        "year": [2010, 2010],
        "month": [1, 2],
        "cases": [12, 18],
    })

    panel = build_panel(weather_df, dengue_df)

    assert len(panel) == 4
    assert list(panel.columns) == [
        "province_en",
        "year",
        "month",
        "cases",
        "temp_mean_c",
        "precip_sum_mm",
        "humidity_mean_pct",
    ]
    # Check that Bueng Kan rows have NA for cases
    bueng_kan_rows = panel[panel["province_en"] == "Bueng Kan"]
    assert len(bueng_kan_rows) == 2
    assert bueng_kan_rows["cases"].isna().all()

    # Check Chiang Mai rows have correct values
    cm_rows = panel[panel["province_en"] == "Chiang Mai"]
    assert cm_rows["cases"].tolist() == [12, 18]


def test_panel_csv_integrity():
    """Verify integrity of processed panel.csv if present."""
    panel_path = Path("data/processed/panel.csv")
    if not panel_path.exists():
        pytest.skip("data/processed/panel.csv not yet generated")

    panel = pd.read_csv(panel_path)

    # Acceptance criteria checks
    assert panel.shape == (27720, 7)
    assert panel.duplicated(subset=["province_en", "year", "month"]).sum() == 0
    assert panel["province_en"].nunique() == 77
    assert panel["year"].min() == 1993
    assert panel["year"].max() == 2022

    # Null counts
    nulls = panel.isna().sum().to_dict()
    assert nulls["province_en"] == 0
    assert nulls["year"] == 0
    assert nulls["month"] == 0
    assert nulls["temp_mean_c"] == 0
    assert nulls["precip_sum_mm"] == 0
    assert nulls["humidity_mean_pct"] == 0
    assert nulls["cases"] == 696  # exactly 696 missing province-months


def test_data_quality_report_exists():
    """Verify data_quality_report.md exists and contains key resolution evidence."""
    report_path = Path("data/processed/data_quality_report.md")
    if not report_path.exists():
        pytest.skip("data/processed/data_quality_report.md not yet generated")

    text = report_path.read_text(encoding="utf-8")
    assert "78" in text
    assert "77" in text
    assert "PHACHINBURI" in text
    assert "PRACHIN BURI" in text
    assert "Bueng Kan" in text
    assert "696" in text
