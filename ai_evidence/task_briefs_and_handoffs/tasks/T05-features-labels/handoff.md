# Handoff — T05 Features, label, time split, and leakage tests
Worker: worker · Date: 2026-11-09 15:33

## What was done
- Implemented `src/features/__init__.py` and `src/features/build_features.py` to produce a leak-free supervised modeling table and per-province threshold table.
- Added strict panel continuity checks verifying that every province has a 360-month gap-free continuous monthly timeline prior to time-series feature generation.
- Fitted historical baseline parameters (`mean_p`, `sd_p`) and outbreak thresholds (`threshold_p = mean_p + 1.0 * sd_p`) strictly on train years (1993–2015) using available train months (276 for 72 regular provinces, 156 for 4 late-starting provinces, 60 for Bueng Kan), writing `data/processed/province_thresholds.csv` (77 rows, 0 NaNs).
- Engineered target at $t+1$ (`target_cases_t1`, `outbreak_t1`) and 27 candidate features strictly from information available at or before month $t$:
  - Case lags: `cases_lag_0`, `cases_lag_1`, `cases_lag_2`, `cases_lag_3`
  - Rolling mean: `cases_roll_mean_3`
  - Standardized case z-score: `cases_zscore_lag_0 = (cases_lag_0 - mean_p) / sd_p`
  - Baseline helper features: `outbreak_lag_0` (current month status), `outbreak_same_month_last_year` ($t-11$ status)
  - Weather lags: `temp_lag_0..3`, `precip_lag_0..3`, `humidity_lag_0..3`
  - Cyclical calendar encoding: `sin_target_month`, `cos_target_month`, `month`, `target_month`
  - Historical province baselines: `mean_p`, `sd_p`, `threshold_p`
- Assigned splits strictly by `target_year`: `train` (1994–2015), `val` (2016–2017), `test` (2018–2022 with `normal`: 2018–2019, `covid`: 2020–2022).
- Cleaned and dropped rows with NaNs (1,620 rows dropped total: 77 missing target $t+1$ at panel end 2022-12, 696 unestablished province months, 847 initial lag-11 months) to yield `data/processed/modeling_table.csv` (26,100 rows, 34 columns, 0 NaNs).
- Generated `results/feature_summary.json` containing class balance and detailed dropped-row accounting, and updated `results/metrics.json`.
- Implemented comprehensive automated tests in `tests/test_features_and_leakage.py` enforcing zero leakage, temporal causality, no-NaN/split completeness, exact math, and summary consistency. All 20 project unit tests pass.

## Files created / changed
- `src/features/__init__.py` (created)
- `src/features/build_features.py` (created)
- `data/processed/province_thresholds.csv` (created)
- `data/processed/modeling_table.csv` (created)
- `results/feature_summary.json` (created)
- `results/metrics.json` (updated)
- `tests/test_features_and_leakage.py` (created)
- `_agent/tasks/T05-features-labels/handoff.md` (created)
- `_agent/logs/WORKLOG.md` (updated)

## Commands run and real output
### 1. `python src/features/build_features.py`
```
Reading panel data from data\processed\panel.csv...
Panel loaded: 27720 rows, 77 provinces.
Computing province thresholds fit strictly on train years...
Saved 77 province thresholds to data\processed\province_thresholds.csv
Building supervised modeling table...
Saved modeling table with shape (26100, 34) to data\processed\modeling_table.csv
Generating feature summary and class balance report...
Saved feature summary to results\feature_summary.json
Updated dataset summary in results\metrics.json

--- Pipeline Summary ---
        rows  provs  min_ty  max_ty  pos_rate
split                                        
test    4620     77    2018    2022    0.0848
train  19632     77    1994    2015    0.0980
val     1848     77    2016    2017    0.0379
------------------------
```

### 2. Criterion 2 verification command
```
python -c "import pandas as pd; m=pd.read_csv('data/processed/modeling_table.csv'); t=pd.read_csv('data/processed/province_thresholds.csv'); print('Thresholds:', t.shape, t.isna().sum().sum()); print('Modeling:', m.shape, m.isna().sum().sum()); print(m.groupby('split').agg(rows=('outbreak_t1','size'), provs=('province_en','nunique'), min_ty=('target_year','min'), max_ty=('target_year','max'), pos_rate=('outbreak_t1','mean')).round(4))"
```
Output:
```
Thresholds: (77, 5) 0
Modeling: (26100, 34) 0
        rows  provs  min_ty  max_ty  pos_rate
split                                        
test    4620     77    2018    2022    0.0848
train  19632     77    1994    2015    0.0980
val     1848     77    2016    2017    0.0379
```

### 3. Leakage unit tests
```
pytest tests/test_features_and_leakage.py -v
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
plugins: anyio-4.14.2
collecting ... collected 5 items

tests/test_features_and_leakage.py::test_train_only_thresholds PASSED    [ 20%]
tests/test_features_and_leakage.py::test_strict_temporal_causality PASSED [ 40%]
tests/test_features_and_leakage.py::test_no_nan_and_split_completeness PASSED [ 60%]
tests/test_features_and_leakage.py::test_feature_engineering_exact_math PASSED [ 80%]
tests/test_features_and_leakage.py::test_feature_summary_json PASSED     [100%]

============================== 5 passed in 4.50s ==============================
```

### 4. Full pytest suite
```
pytest -v
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0 -- C:\Users\User\AppData\Local\Programs\Python\Python313\python.exe
cachedir: .pytest_cache
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
plugins: anyio-4.14.2
collecting ... collected 20 items

tests/test_build_panel.py::test_province_map_structure_and_coverage PASSED [  5%]
tests/test_build_panel.py::test_build_panel_merge_logic PASSED           [ 10%]
tests/test_build_panel.py::test_panel_csv_integrity PASSED               [ 15%]
tests/test_build_panel.py::test_data_quality_report_exists PASSED        [ 20%]
tests/test_eda.py::test_figures_exist_and_non_empty PASSED               [ 25%]
tests/test_eda.py::test_eda_stats_json_valid_and_structured PASSED       [ 30%]
tests/test_eda.py::test_lag_correlations_computed_strictly_on_train_years PASSED [ 35%]
tests/test_eda.py::test_province_heterogeneity_train_years_strictly PASSED [ 40%]
tests/test_eda.py::test_seasonality_peak_months_train_years PASSED       [ 45%]
tests/test_features_and_leakage.py::test_train_only_thresholds PASSED    [ 50%]
tests/test_features_and_leakage.py::test_strict_temporal_causality PASSED [ 55%]
tests/test_features_and_leakage.py::test_no_nan_and_split_completeness PASSED [ 60%]
tests/test_features_and_leakage.py::test_feature_engineering_exact_math PASSED [ 65%]
tests/test_features_and_leakage.py::test_feature_summary_json PASSED     [ 70%]
tests/test_province_centroids.py::test_province_centroids_file_exists PASSED [ 75%]
tests/test_province_centroids.py::test_province_centroids_structure_and_counts PASSED [ 80%]
tests/test_province_centroids.py::test_province_centroids_coordinate_bounds PASSED [ 85%]
tests/test_province_centroids.py::test_key_provinces_present PASSED      [ 90%]
tests/test_weather.py::test_slugify_name PASSED                          [ 95%]
tests/test_weather.py::test_aggregate_daily_to_monthly PASSED            [100%]

============================= 20 passed in 8.76s ==============================
```

## Results
- Total panel input rows: `27,720` (77 provinces × 360 months)
- Total dropped rows: `1,620`
  - Regular provinces initial lag-11: `792` (72 provinces × 11 months, 1993-01 to 1993-11)
  - 4 late-starting provinces pre-establishment: `480` (4 × 120 months, 1993-01 to 2002-12)
  - 4 late-starting provinces initial lag-11: `44` (4 × 11 months, 2003-01 to 2003-11)
  - Bueng Kan pre-establishment: `216` (1 × 216 months, 1993-01 to 2010-12)
  - Bueng Kan initial lag-11: `11` (1 × 11 months, 2011-01 to 2011-11)
  - End of panel missing target $t+1$: `77` (77 provinces × 1 month, 2022-12)
- Clean modeling table rows: `26,100` (0 NaNs across all 34 columns)
  - `train`: `19,632` rows, `77` provinces, min target year `1994`, max target year `2015`, `1,923` positive outbreaks (prevalence `9.80%`)
  - `val`: `1,848` rows, `77` provinces, min target year `2016`, max target year `2017`, `70` positive outbreaks (prevalence `3.79%`)
  - `test`: `4,620` rows, `77` provinces, min target year `2018`, max target year `2022`, `392` positive outbreaks (prevalence `8.48%`)
    - `test_normal_2018_2019`: `1,848` rows, `77` provinces, `269` positive outbreaks (prevalence `14.56%`)
    - `test_covid_2020_2022`: `2,772` rows, `77` provinces, `123` positive outbreaks (prevalence `4.44%`)

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/features/build_features.py` runs to completion with exit code 0 | PASS | Exited 0; generated thresholds, modeling table, feature summary, metrics |
| 2 | Verification command outputs 77 thresholds (0 NaNs), modeling table (0 NaNs), val (1,848 rows), test (4,620 rows) | PASS | `Thresholds: (77, 5) 0`, `Modeling: (26100, 34) 0`, `val` has 1,848 rows, `test` has 4,620 rows |
| 3 | `tests/test_features_and_leakage.py` passes train-only threshold test, causality test, no-NaN/split completeness | PASS | All 5 test cases in `test_features_and_leakage.py` passed |
| 4 | `pytest` passes all project tests | PASS | 20 passed in 8.76s across all test suites |

## Deviations from the brief
None.

## UNVERIFIED items
None.

## SSOT change requests
None.

## Suggested next steps
- Review T05 handoff and mark T05 as PASS in `_agent/tasks/INDEX.md`.
- Unlock and brief T06 (Baselines: majority class, same flag as this month `outbreak_lag_0`, and same calendar month last year `outbreak_same_month_last_year`).
