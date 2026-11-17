"""Tests for weather fetching and aggregation functions."""

import numpy as np
import pandas as pd
import pytest
from src.data.fetch_weather import aggregate_daily_to_monthly, slugify_name


def test_slugify_name():
    """Verify name sanitization for cache filenames."""
    assert slugify_name("Bangkok") == "bangkok"
    assert slugify_name("Chiang Mai") == "chiang_mai"
    assert slugify_name("Phra Nakhon Si Ayutthaya") == "phra_nakhon_si_ayutthaya"
    assert slugify_name("  Ubon Ratchathani  ") == "ubon_ratchathani"


def test_aggregate_daily_to_monthly():
    """Verify daily aggregation logic matches SSOT rules."""
    daily_data = {
        "time": [
            "2020-01-01",
            "2020-01-02",
            "2020-01-03",
            "2020-02-01",
            "2020-02-02",
        ],
        "temperature_2m_mean": [26.0, 28.0, 30.0, 25.0, 27.0],
        "precipitation_sum": [1.5, 3.5, 0.0, 10.0, 5.0],
        "relative_humidity_2m_mean": [70.0, 75.0, 80.0, 60.0, 65.0],
    }

    monthly = aggregate_daily_to_monthly(daily_data, province="TestProvince")

    assert len(monthly) == 2
    assert list(monthly.columns) == [
        "province_en",
        "year",
        "month",
        "temp_mean_c",
        "precip_sum_mm",
        "humidity_mean_pct",
    ]

    # Month 1: Jan 2020
    jan = monthly[monthly["month"] == 1].iloc[0]
    assert jan["province_en"] == "TestProvince"
    assert jan["year"] == 2020
    assert pytest.approx(jan["temp_mean_c"], 1e-4) == 28.0  # mean(26, 28, 30)
    assert pytest.approx(jan["precip_sum_mm"], 1e-4) == 5.0  # sum(1.5, 3.5, 0.0)
    assert pytest.approx(jan["humidity_mean_pct"], 1e-4) == 75.0  # mean(70, 75, 80)

    # Month 2: Feb 2020
    feb = monthly[monthly["month"] == 2].iloc[0]
    assert feb["year"] == 2020
    assert pytest.approx(feb["temp_mean_c"], 1e-4) == 26.0  # mean(25, 27)
    assert pytest.approx(feb["precip_sum_mm"], 1e-4) == 15.0  # sum(10.0, 5.0)
    assert pytest.approx(feb["humidity_mean_pct"], 1e-4) == 62.5  # mean(60, 65)
