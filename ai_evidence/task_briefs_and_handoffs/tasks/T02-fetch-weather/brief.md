# Brief — T02 Fetch monthly weather per province + centroid table
Status: TODO · Written by: orchestrator · Date: 2026-11-08

## Goal
Build a table of Thai province centroid coordinates, then fetch daily weather from Open-Meteo for 1993-01-01 to 2022-12-31 for each province and aggregate to monthly.

## Why
Serves R2, R3 (weather features: rain and temperature). Depends on: T00. Can run in parallel with T01.

## Inputs
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api — **read the docs first**; the endpoint, variable names, rate limits and license are UNVERIFIED in the SSOT. Verify with a single test call before looping.
- Province list: the 77 Thai provinces (including Bangkok). Use English names that can later be matched to OpenDengue `adm_1_name` (uppercase in OpenDengue, e.g. `CHIANG RAI`, `PHRA NAKHON SI AYUDHYA`).

## Outputs
- `src/data/province_centroids.csv` — columns: `province_en, lat, lon, source`. 77 rows. Record the public source of coordinates (name + URL) in the `source` column. Do not guess coordinates from memory; take them from a downloadable public dataset and spot-check 5 provinces against a map source.
- `src/data/fetch_weather.py` — idempotent; caches per-province responses in `data/raw/weather_cache/`; sleeps between calls to respect rate limits; retries on failure.
- `data/raw/weather_monthly.csv` — columns: `province_en, year, month, temp_mean_c, precip_sum_mm` (+ `humidity_mean_pct` only if the API provides a daily mean variable; otherwise skip and say so).
- `data/raw/SOURCE_weather.md` — API URL and parameters used, date, license/terms quoted from the Open-Meteo page (with URL), how monthly aggregation was done.

## Constraints
- Monthly aggregation: `temp_mean_c` = mean of daily means; `precip_sum_mm` = sum of daily precipitation.
- Use only documented variable names. If a name errors, report it, do not invent.
- No API keys. Free non-commercial endpoint only.

## Out of scope
Matching province names to OpenDengue (T03), feature lags (T05).

## Acceptance criteria (paste real output)
1. `python src/data/fetch_weather.py` completes (may take several minutes).
2. `python -c "import pandas as pd; d=pd.read_csv('data/raw/weather_monthly.csv'); print(d.shape, d.province_en.nunique(), d.isna().sum().to_dict(), d.year.min(), d.year.max())"` → expected: 27,720 rows (77 × 360), 77 provinces, no NaN, 1993 to 2022.
3. Centroid file has 77 unique provinces and plausible ranges (lat 5–21, lon 97–106).
4. `SOURCE_weather.md` has the quoted license/terms.

## Known pitfalls
- Daily precipitation in Open-Meteo may be per-model-grid-cell, not station data. Note this limitation in `SOURCE_weather.md`.
- Bangkok is named differently across sources (Krung Thep Maha Nakhon, Bangkok). Record the name you used.
