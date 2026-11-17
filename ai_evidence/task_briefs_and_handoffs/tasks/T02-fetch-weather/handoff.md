# Handoff — T02 Fetch monthly weather per province + centroid table
Worker: worker · Date: 2026-11-09 14:50

## What was done
1. Built `src/data/province_centroids.csv` containing coordinates for all 77 Thai provinces derived from public open GIS dataset (`OpenGISData-Thailand / provinces.geojson` by Chingchai Humhong), calculated using Lambert Azimuthal Equal Area (LAEA) projection on WGS84 ellipsoid.
2. Verified coordinate plausibility (latitudes 6.18–19.85°N, longitudes 98.03–105.11°E) and spot-checked 5 provinces (Bangkok, Chiang Mai, Phuket, Ubon Ratchathani, Songkhla) against ground-truth map references.
3. Implemented `src/data/fetch_weather.py` with:
   - Persistent `requests.Session()` to avoid socket proliferation and "Too many concurrent requests" errors.
   - Proactive minute-window rate management (`OpenMeteoRateManager`) respecting Open-Meteo's 600 calls/minute limit.
   - Exponential backoff and retries on transient errors or HTTP 429.
   - Per-province local disk caching in `data/raw/weather_cache/{province_slug}.json` for full idempotency.
   - Aggregation of daily reanalysis weather (`temperature_2m_mean`, `precipitation_sum`, `relative_humidity_2m_mean`) to calendar-month averages (`temp_mean_c`, `precip_sum_mm`, `humidity_mean_pct`).
4. Downloaded daily weather for all 77 provinces covering 1993-01-01 to 2022-12-31 (10,957 days per province; 843,689 daily records total).
5. Combined and validated the monthly weather panel saving `27,720` rows to `data/raw/weather_monthly.csv` with zero NaNs.
6. Generated `data/raw/SOURCE_weather.md` documenting API parameters, exact quoted CC BY 4.0 license, non-commercial free tier terms, centroid methodology, spot checks, and pitfalls (reanalysis grid vs station observations, centroid approximation, Bangkok naming).
7. Added unit test suites `tests/test_province_centroids.py` and `tests/test_weather.py` (6 passing tests).

## Files created / changed
- `src/data/province_centroids.csv`
- `src/data/fetch_weather.py`
- `tests/test_province_centroids.py`
- `tests/test_weather.py`
- `pytest.ini`
- `data/raw/weather_cache/*.json` (77 files, git-ignored)
- `data/raw/weather_monthly.csv` (git-ignored)
- `data/raw/SOURCE_weather.md` (git-ignored)
- `_agent/tasks/T02-fetch-weather/handoff.md`
- `_agent/logs/WORKLOG.md`

## Commands run and real output

### 1. Verification of weather_monthly.csv (Acceptance Criterion 2)
Command:
```bash
python -c "import pandas as pd; d=pd.read_csv('data/raw/weather_monthly.csv'); print(d.shape, d.province_en.nunique(), d.isna().sum().to_dict(), d.year.min(), d.year.max())"
```
Output:
```
(27720, 6) 77 {'province_en': 0, 'year': 0, 'month': 0, 'temp_mean_c': 0, 'precip_sum_mm': 0, 'humidity_mean_pct': 0} 1993 2022
```

### 2. Verification of province_centroids.csv (Acceptance Criterion 3)
Command:
```bash
python -c "import pandas as pd; c=pd.read_csv('src/data/province_centroids.csv'); print(c.shape, c['province_en'].nunique(), c['lat'].min(), c['lat'].max(), c['lon'].min(), c['lon'].max(), c.isna().sum().to_dict())"
```
Output:
```
(77, 4) 77 6.177906 19.8469 98.02996 105.110829 {'province_en': 0, 'lat': 0, 'lon': 0, 'source': 0}
```

### 3. Pipeline idempotency test (Acceptance Criterion 1)
Command:
```bash
python src/data/fetch_weather.py
```
Output:
```
--- Step 1: Ensure province centroids table ---
Loaded 77 provinces from src\data\province_centroids.csv

--- Step 2: Fetch daily weather for 77 provinces (1993-2022) ---
[1/77] Processing Amnat Charoen...
  [Cache hit] Amnat Charoen (10957 daily records)
[2/77] Processing Ang Thong...
  [Cache hit] Ang Thong (10957 daily records)
...
[76/77] Processing Yala...
  [Cache hit] Yala (10957 daily records)
[77/77] Processing Yasothon...
  [Cache hit] Yasothon (10957 daily records)

--- Step 3: Combine and validate monthly panel ---
Saved 27720 rows to data\raw\weather_monthly.csv

--- Step 4: Write SOURCE metadata ---
Saved source metadata to data\raw\SOURCE_weather.md

--- Verification Summary ---
Shape: (27720, 6)
Provinces: 77
Null counts: {'province_en': 0, 'year': 0, 'month': 0, 'temp_mean_c': 0, 'precip_sum_mm': 0, 'humidity_mean_pct': 0}
Year range: 1993 to 2022
SUCCESS: Weather data pipeline complete.
```
(Executed in ~4.0 seconds with 77 cache hits).

### 4. Unit test suite execution
Command:
```bash
pytest
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2
collected 6 items

tests\test_province_centroids.py ....                                    [ 66%]
tests\test_weather.py ..                                                 [100%]

============================== 6 passed in 0.74s ==============================
```

## Results
- Centroid records: `77` provinces
- Latitude range: `6.177906` to `19.846900`
- Longitude range: `98.029960` to `105.110829`
- Weather panel shape: `(27720, 6)`
- Months per province: `360` (12 months × 30 years)
- Year range: `1993` to `2022`
- Missing values: `0` across all metrics (`province_en`, `year`, `month`, `temp_mean_c`, `precip_sum_mm`, `humidity_mean_pct`)

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/data/fetch_weather.py` completes | PASS | Runs cleanly; cached re-run finishes in ~4s with exit code 0 |
| 2 | Shape `(27720, 6)`, 77 provinces, no NaN, 1993 to 2022 | PASS | Real output: `(27720, 6) 77 {'province_en': 0, 'year': 0, 'month': 0, 'temp_mean_c': 0, 'precip_sum_mm': 0, 'humidity_mean_pct': 0} 1993 2022` |
| 3 | Centroid file has 77 unique provinces and plausible ranges (lat 5–21, lon 97–106) | PASS | Output: `77` unique, lat `[6.177906, 19.846900]`, lon `[98.029960, 105.110829]`, 0 NaNs |
| 4 | `SOURCE_weather.md` has the quoted license/terms | PASS | Contains quoted CC BY 4.0 license, non-commercial free tier limits, attribution text, methodology, and limitations |

## Deviations from the brief
None.

## UNVERIFIED items
None.

## SSOT change requests
Propose updating `_agent/docs/SSOT.md` §3 ("Weather — Open-Meteo Historical Weather API"):
- Mark Open-Meteo API endpoint as `VERIFIED (2026-11-09, code)`: `https://archive-api.open-meteo.com/v1/archive`
- Variables verified: `temperature_2m_mean` (°C), `precipitation_sum` (mm), `relative_humidity_2m_mean` (%)
- Terms & license verified: CC BY 4.0; non-commercial free tier (600 calls/min, 5,000 calls/hr, 10,000 calls/day per IP; weighted cost per call scales with variables and duration)
- Province centroids: `src/data/province_centroids.csv` (77 rows, derived from `OpenGISData-Thailand / provinces.geojson`, area-weighted LAEA centroid calculation).

## Suggested next steps
Reviewer checks T02 against criteria. Once PASS, unlock T03 (`clean-merge`).
