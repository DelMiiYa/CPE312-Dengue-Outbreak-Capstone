# Handoff — T06 Build and evaluate the 3 baseline classifiers
Worker: worker · Date: 2026-11-09 15:46

## What was done
- Implemented `src/models/__init__.py` and `src/models/baselines.py` to evaluate the 3 locked baselines from SSOT §2 (`majority_class`, `persistence_last_month`, `seasonal_last_year`) across all 5 required splits (`train`, `val`, `test`, `test_normal_2018_2019`, and `test_covid_2020_2022`).
- Preserved existing `"dataset"` metadata and updated `results/metrics.json` under top-level key `"baselines"` with comprehensive metrics (`recall`, `precision`, `f1`, `pr_auc`, `specificity`, `accuracy`, `tp`, `fp`, `tn`, `fn`, `support_pos`, `support_total`, and auxiliary `pr_auc_continuous_zscore` for persistence).
- Generated `results/baselines_report.md` comparing all baselines strictly using data from `results/metrics.json`.
- Implemented comprehensive unit tests in `tests/test_baselines.py` validating split shapes, confusion matrix identities, mathematical bounds, metric formulas, and report consistency.

## Files created / changed
- `src/models/__init__.py` (created)
- `src/models/baselines.py` (created)
- `results/metrics.json` (updated with `"baselines"` key; preserved `"dataset"`)
- `results/baselines_report.md` (created)
- `tests/test_baselines.py` (created)
- `_agent/tasks/T06-baselines/handoff.md` (created)

## Commands run and real output

### 1. Baselines script execution
```
Loading modeling table from data\processed\modeling_table.csv...
Evaluating 3 locked baselines across all splits...
Updating metrics in results\metrics.json...
Generating baselines comparison report in results\baselines_report.md...
Baselines evaluation completed successfully.
```

### 2. Verification of results/metrics.json contents
Command:
```bash
python -c "import json; m=json.load(open('results/metrics.json')); print('Keys:', list(m.keys())); print('Baselines:', list(m['baselines'].keys())); [print(b, s, {k: round(v,4) if isinstance(v,float) else v for k,v in m['baselines'][b][s].items() if k in ['recall','precision','f1','pr_auc','tp','fp','fn']}) for b in m['baselines'] for s in ['val','test','test_normal_2018_2019','test_covid_2020_2022']]"
```
Real output:
```
Keys: ['dataset', 'baselines']
Baselines: ['majority_class', 'persistence_last_month', 'seasonal_last_year']
majority_class val {'recall': 0.0, 'precision': 0.0, 'f1': 0.0, 'pr_auc': 0.0379, 'tp': 0, 'fp': 0, 'fn': 70}
majority_class test {'recall': 0.0, 'precision': 0.0, 'f1': 0.0, 'pr_auc': 0.0848, 'tp': 0, 'fp': 0, 'fn': 392}
majority_class test_normal_2018_2019 {'recall': 0.0, 'precision': 0.0, 'f1': 0.0, 'pr_auc': 0.1456, 'tp': 0, 'fp': 0, 'fn': 269}
majority_class test_covid_2020_2022 {'recall': 0.0, 'precision': 0.0, 'f1': 0.0, 'pr_auc': 0.0444, 'tp': 0, 'fp': 0, 'fn': 123}
persistence_last_month val {'recall': 0.6, 'precision': 0.5385, 'f1': 0.5676, 'pr_auc': 0.3382, 'tp': 42, 'fp': 36, 'fn': 28}
persistence_last_month test {'recall': 0.6224, 'precision': 0.6321, 'f1': 0.6272, 'pr_auc': 0.4255, 'tp': 244, 'fp': 142, 'fn': 148}
persistence_last_month test_normal_2018_2019 {'recall': 0.6208, 'precision': 0.6208, 'f1': 0.6208, 'pr_auc': 0.4406, 'tp': 167, 'fp': 102, 'fn': 102}
persistence_last_month test_covid_2020_2022 {'recall': 0.626, 'precision': 0.6581, 'f1': 0.6417, 'pr_auc': 0.4286, 'tp': 77, 'fp': 40, 'fn': 46}
seasonal_last_year val {'recall': 0.2571, 'precision': 0.0652, 'f1': 0.104, 'pr_auc': 0.0449, 'tp': 18, 'fp': 258, 'fn': 52}
seasonal_last_year test {'recall': 0.2832, 'precision': 0.2984, 'f1': 0.2906, 'pr_auc': 0.1453, 'tp': 111, 'fp': 261, 'fn': 281}
seasonal_last_year test_normal_2018_2019 {'recall': 0.1933, 'precision': 0.4333, 'f1': 0.2674, 'pr_auc': 0.2012, 'tp': 52, 'fp': 68, 'fn': 217}
seasonal_last_year test_covid_2020_2022 {'recall': 0.4797, 'precision': 0.2341, 'f1': 0.3147, 'pr_auc': 0.1354, 'tp': 59, 'fp': 193, 'fn': 64}
```

### 3. Pytest test suite
Command:
```bash
pytest
```
Real output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2
collected 28 items

tests\test_baselines.py ........                                         [ 28%]
tests\test_build_panel.py ....                                           [ 42%]
tests\test_eda.py .....                                                  [ 60%]
tests\test_features_and_leakage.py .....                                 [ 78%]
tests\test_province_centroids.py ....                                    [ 92%]
tests\test_weather.py ..                                                 [100%]

============================= 28 passed in 9.87s ==============================
```

## Results
Key baseline metrics on `val` (2016–2017) and `test` overall (2018–2022):

| Baseline | Split | Recall (R1 Main) | Precision | F1 | PR-AUC | Accuracy | Specificity | TP / Pos Support | Total Rows |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `majority_class` | `val` | 0.0000 | 0.0000 | 0.0000 | 0.0379 | 0.9621 | 1.0000 | 0 / 70 | 1848 |
| `majority_class` | `test` | 0.0000 | 0.0000 | 0.0000 | 0.0848 | 0.9152 | 1.0000 | 0 / 392 | 4620 |
| `persistence_last_month` | `val` | 0.6000 | 0.5385 | 0.5676 | 0.3382 | 0.9654 | 0.9798 | 42 / 70 | 1848 |
| `persistence_last_month` | `test` | 0.6224 | 0.6321 | 0.6272 | 0.4255 | 0.9372 | 0.9664 | 244 / 392 | 4620 |
| `persistence_last_month` (cont. z-score) | `val` | - | - | - | 0.5898 | - | - | - | 1848 |
| `persistence_last_month` (cont. z-score) | `test` | - | - | - | 0.6907 | - | - | - | 4620 |
| `seasonal_last_year` | `val` | 0.2571 | 0.0652 | 0.1040 | 0.0449 | 0.8323 | 0.8549 | 18 / 70 | 1848 |
| `seasonal_last_year` | `test` | 0.2832 | 0.2984 | 0.2906 | 0.1453 | 0.8827 | 0.9383 | 111 / 392 | 4620 |

Key subperiod breakdown for Test set:
- **Test Normal (2018–2019, 1,848 rows, 269 outbreaks):**
  - Persistence Recall: 0.6208 (167/269), Precision: 0.6208, F1: 0.6208
  - Seasonal Recall: 0.1933 (52/269), Precision: 0.4333, F1: 0.2674
- **Test COVID-era (2020–2022, 2,772 rows, 123 outbreaks):**
  - Persistence Recall: 0.6260 (77/123), Precision: 0.6581, F1: 0.6417
  - Seasonal Recall: 0.4797 (59/123), Precision: 0.2341, F1: 0.3147

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/models/baselines.py` runs to completion with exit code 0 | PASS | Exited code 0 without errors; logs shown above |
| 2 | Python verification command checks keys and baseline split metrics | PASS | Output shows keys `['dataset', 'baselines']` and all 3 baselines across splits with exact numbers |
| 3 | Every number in `results/baselines_report.md` matches `results/metrics.json` | PASS | Automated regex assertion verified 100% concordance |
| 4 | `pytest` passes all unit tests including `tests/test_baselines.py` | PASS | 28/28 tests passed in 9.87s |

## Deviations from the brief
None.

## UNVERIFIED items
None.

## SSOT change requests
None.

## Suggested next steps
- Reviewer checks T06 (review `src/models/baselines.py`, `results/metrics.json`, `results/baselines_report.md`, and `tests/test_baselines.py`).
- Proceed to T07 (Supervised ML models: Logistic Regression, Random Forest / HistGradientBoosting, tuning on validation set, aiming to beat the persistence baseline recall benchmark of 0.6000 on val and 0.6224 on test).
