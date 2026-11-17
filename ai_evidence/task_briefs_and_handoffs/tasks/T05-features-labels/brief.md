# Brief — T05 Feature engineering, outbreak label, time split, and leakage tests
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Build the leak-free supervised learning table (`data/processed/modeling_table.csv`) and per-province threshold table (`data/processed/province_thresholds.csv`), and verify strict temporal causality and train-only threshold fitting with automated unit tests.

## Why
Serves requirement(s): R1 (prediction timing, target definition, no data leakage) and R2 (time-based train/val/test split, handling of late-starting provinces). Depends on: T03 (PASS). Can run in parallel with T04.

## Inputs (exact paths)
- `data/processed/panel.csv`
- `config/params.yaml`

## Outputs (exact paths)
- `src/features/__init__.py`
- `src/features/build_features.py` — idempotent feature & label pipeline
- `data/processed/province_thresholds.csv` — columns: `province_en, train_months, mean_p, sd_p, threshold_p` (77 rows)
- `data/processed/modeling_table.csv` — complete supervised dataset ready for T06/T07
- `results/feature_summary.json` — row counts, class balance (`outbreak_t1` prevalence) by split (`train`, `val`, `test`, `test_normal_2018_2019`, `test_covid_2020_2022`), feature list, and dropped-row accounting
- `tests/test_features_and_leakage.py` — automated tests enforcing zero data leakage and strict time splits

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`.
- Read all parameters (`horizon_months`, `outbreak_k`, `split`, `features`) from `config/params.yaml`.
- **Sort order:** Always sort by `['province_en', 'year', 'month']` and verify consecutive monthly steps before shifting.
- **Per-province threshold (fit on train years only):**
  - For each province $p$, filter to rows where `train_years[0] <= year <= train_years[1]` (`1993 <= year <= 2015`) and `cases` is non-null.
  - Compute `mean_p = cases.mean()`, `sd_p = cases.std(ddof=1)`, and `threshold_p = mean_p + outbreak_k * sd_p` (`k = 1.0`).
  - As recommended in T03, late-starting provinces use their available train months (`2003–2015` for Amnat Charoen, Mukdahan, Nong Bua Lamphu, Sa Kaeo; `2011–2015` for Bueng Kan).
- **Target at row $(p, t)$:**
  - `target_year`, `target_month`: calendar year and month of $t+1$.
  - `target_cases_t1`: `cases` at $(p, t+1)$ (`groupby('province_en')['cases'].shift(-1)`).
  - `outbreak_t1`: `1` if `target_cases_t1 > threshold_p` else `0` (nullable where `target_cases_t1` is `NA`, such as `2022-12` or prior to a province's start date).
- **Features at row $(p, t)$ (strictly from month $\le t$ within province $p$):**
  - Case lag features (from `case_lags: [1, 2, 3]` plus current month `0`):
    - `cases_lag_0` (cases at month $t$), `cases_lag_1` ($t-1$), `cases_lag_2` ($t-2$), `cases_lag_3` ($t-3$).
    - `cases_roll_mean_3`: rolling 3-month mean of cases ending at month $t$ (i.e. mean of $t, t-1, t-2$, `min_periods=3`).
    - `cases_zscore_lag_0`: `(cases_lag_0 - mean_p) / sd_p` (standardized current cases using train-only `mean_p`, `sd_p`).
  - Baseline helper columns (strictly from month $\le t$, used by T06 baselines and available as features):
    - `outbreak_lag_0`: `1` if `cases_lag_0 > threshold_p` else `0` (current month's outbreak status, i.e., "same flag as this month" baseline).
    - `outbreak_same_month_last_year`: outbreak flag of month $(t+1) - 12 = t - 11$, i.e. `1` if `cases(p, t-11) > threshold_p` else `0` ("same calendar month last year" baseline for target month $t+1$).
  - Weather lag features (from `weather_lags: [0, 1, 2, 3]`):
    - `temp_lag_0`, `temp_lag_1`, `temp_lag_2`, `temp_lag_3`
    - `precip_lag_0`, `precip_lag_1`, `precip_lag_2`, `precip_lag_3`
    - `humidity_lag_0`, `humidity_lag_1`, `humidity_lag_2`, `humidity_lag_3`
  - Calendar & province scale features:
    - `month` (month of $t$, `1..12`), `target_month` (month of $t+1$, `1..12`), `sin_target_month` ($\sin(2\pi \cdot \text{target\_month}/12)$), `cos_target_month` ($\cos(2\pi \cdot \text{target\_month}/12)$)
    - `mean_p`, `sd_p` (train-only province historical baseline)
- **Split assignment & row filtering:**
  - Assign `split` by the **target year** (`target_year`, the year of month $t+1$ being predicted) OR by prediction year (`year`)—Wait: to be 100% explicit and unambiguous, assign `split` by **prediction year `year`** (`1993–2015` -> `train`, `2016–2017` -> `val`, `2018–2022` -> `test`) AND record `subperiod` (`normal` for `2018 <= year <= 2019`, `covid` for `2020 <= year <= 2022`, `none` otherwise). Note: for `year == 2015, month == 12`, `target_cases_t1` is `2016-01`; to guarantee **zero overlap between train targets and val/test years**, verify that `threshold_p` is computed on `1993 <= year <= 2015` `cases(p, t)` only, and check whether assigning `split` by `target_year` (`1993–2015` train, `2016–2017` val, `2018–2022` test) is cleaner because then every target month `t+1` in `val` is strictly in `2016–2017` and every target month `t+1` in `test` is strictly in `2018–2022` (including `2018-01` predicted from `2017-12`, and `2022-12` predicted from `2022-11`!).
  - **Use `target_year` for `split` assignment** (`1993 <= target_year <= 2015` → `train`; `2016 <= target_year <= 2017` → `val`; `2018 <= target_year <= 2022` → `test`, with `subperiod = 'normal'` for `2018 <= target_year <= 2019` and `'covid'` for `2020 <= target_year <= 2022`). Why? Because the question is *"Will dengue break out in month $t+1$?"*, so all 12 months of 2016–2017 (24 months × 77 provinces = 1,848 rows) are evaluated in `val`, and all 60 months of 2018–2022 (60 months × 77 provinces = 4,620 rows) are evaluated in `test` with zero missing targets!
  - Drop rows from `modeling_table.csv` where `outbreak_t1` or any feature column (including `outbreak_same_month_last_year`, which requires $t-11$) is `NaN`, and record the exact dropped-row breakdown in `results/feature_summary.json`.

## Out of scope
Training models or evaluating baselines (covered in T06 and T07).

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/features/build_features.py` runs to completion with exit code 0.
2. `python -c "import pandas as pd; m=pd.read_csv('data/processed/modeling_table.csv'); t=pd.read_csv('data/processed/province_thresholds.csv'); print('Thresholds:', t.shape, t.isna().sum().sum()); print('Modeling:', m.shape, m.isna().sum().sum()); print(m.groupby('split').agg(rows=('outbreak_t1','size'), provs=('province_en','nunique'), min_ty=('target_year','min'), max_ty=('target_year','max'), pos_rate=('outbreak_t1','mean')).round(4))"`
   → expected: 77 thresholds with 0 NaNs; modeling table with 0 NaNs; `val` has 1,848 rows (77 × 24, target years 2016–2017); `test` has 4,620 rows (77 × 60, target years 2018–2022).
3. `tests/test_features_and_leakage.py` includes and passes:
   - **Train-only threshold test:** modifying `cases` in years `>= 2016` does not change `province_thresholds.csv` at all.
   - **Strict temporal causality test:** modifying `cases` or weather at month $t+1$ does not change any feature column at row $t$.
   - **No-NaN and split completeness test:** `val` (1,848 rows) and `test` (4,620 rows) cover all 77 provinces with 0 NaNs.
4. `pytest` passes all project tests.

## Known pitfalls
- Do not compute rolling means or shifts before grouping by `province_en`.
- When shifting by `-1` or `+k`, verify that the panel is a complete monthly grid per province so `shift(k)` always corresponds to exactly `k` calendar months.
