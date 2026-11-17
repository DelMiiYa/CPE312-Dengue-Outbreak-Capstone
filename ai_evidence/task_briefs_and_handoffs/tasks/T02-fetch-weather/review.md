# Review — T02 Fetch monthly weather per province + centroid table
Reviewer: orchestrator/reviewer · Date: 2026-11-09

## Verdict
PASS (after minor reviewer doc fix in `src/data/fetch_weather.py` and `data/raw/SOURCE_weather.md`)

## Checks run
| Check | Result |
|---|---|
| Acceptance check 1: `python src/data/fetch_weather.py` idempotency run | PASS — 77 cache hits (`data/raw/weather_cache/*.json`, 10,957 daily records each), exited 0 |
| Acceptance check 2: `data/raw/weather_monthly.csv` shape, province count, NaNs, year range | PASS — `(27720, 6) 77 {'province_en': 0, 'year': 0, 'month': 0, 'temp_mean_c': 0, 'precip_sum_mm': 0, 'humidity_mean_pct': 0} 1993 2022` |
| Acceptance check 3: `src/data/province_centroids.csv` shape, uniqueness, bounds | PASS — `(77, 4)`, 77 unique provinces, lat `6.177906`–`19.846900`, lon `98.029960`–`105.110829`, 0 NaNs |
| Acceptance check 4: `data/raw/SOURCE_weather.md` license, terms, aggregation method, limitations | PASS — quotes Open-Meteo `CC BY 4.0` license and non-commercial free tier limits |
| Unit tests (`pytest`) | PASS — 6 passed in `tests/test_province_centroids.py` and `tests/test_weather.py` |
| Cross-check `OpenGISData-Thailand/provinces.geojson` against `ensure_centroids_csv()` and `SOURCE_weather.md` | Caught doc hallucination (fixed during review; logged for R7) |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| 1 | `src/data/fetch_weather.py:321-324` & `data/raw/SOURCE_weather.md:53-56` | Worker claimed centroids were computed by reprojecting polygons to LAEA using `shapely` and `pyproj/PROJ`, whereas `ensure_centroids_csv()` (`src/data/fetch_weather.py:70-77`) directly reads the precomputed `properties.lat` and `properties.lon` fields from `OpenGISData-Thailand/provinces.geojson`. | Fixed directly by reviewer in `src/data/fetch_weather.py` and regenerated `data/raw/SOURCE_weather.md`; logged in `WORKLOG.md` as an **R7 AI-correction example**. |

## Hallucination check
- Every claimed file/column/number verified against real output? yes (all numbers verified; prose claim about LAEA/shapely corrected to match code)
- Anything in handoff contradicting SSOT? no

## Notes for orchestrator
- Both `T01` and `T02` are now `PASS`. `T03` (`clean-merge`) is unlocked.
- Pending SSOT updates from `T02`: mark Open-Meteo endpoint (`https://archive-api.open-meteo.com/v1/archive`), variables (`temperature_2m_mean`, `precipitation_sum`, `relative_humidity_2m_mean`), license (`CC BY 4.0`, non-commercial free tier), and `src/data/province_centroids.csv` as `VERIFIED (2026-11-09)`.
