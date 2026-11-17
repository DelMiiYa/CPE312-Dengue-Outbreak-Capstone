"""Tests for province centroids dataset."""

from pathlib import Path
import pandas as pd
import pytest

CENTROIDS_PATH = Path("src/data/province_centroids.csv")


def test_province_centroids_file_exists():
    """Verify that province_centroids.csv exists."""
    assert CENTROIDS_PATH.exists(), f"Centroids file not found at {CENTROIDS_PATH}"


def test_province_centroids_structure_and_counts():
    """Verify columns, row count, uniqueness, and null values."""
    df = pd.read_csv(CENTROIDS_PATH)
    assert len(df) == 77, f"Expected 77 provinces, got {len(df)}"
    assert set(df.columns) == {"province_en", "lat", "lon", "source"}
    assert df["province_en"].nunique() == 77, "Province names must be unique"
    assert df.isna().sum().sum() == 0, f"Found unexpected null values: {df.isna().sum().to_dict()}"


def test_province_centroids_coordinate_bounds():
    """Verify that lat and lon fall within plausible bounds for Thailand (lat 5–21, lon 97–106)."""
    df = pd.read_csv(CENTROIDS_PATH)
    assert df["lat"].between(5.0, 21.0).all(), "Latitude values out of expected bounds [5, 21]"
    assert df["lon"].between(97.0, 106.0).all(), "Longitude values out of expected bounds [97, 106]"


def test_key_provinces_present():
    """Verify key provinces are present with correct naming."""
    df = pd.read_csv(CENTROIDS_PATH)
    provinces = set(df["province_en"])
    expected_sample = {
        "Bangkok",
        "Chiang Mai",
        "Phuket",
        "Ubon Ratchathani",
        "Songkhla",
        "Bueng Kan",
    }
    assert expected_sample.issubset(provinces), f"Missing key provinces: {expected_sample - provinces}"
