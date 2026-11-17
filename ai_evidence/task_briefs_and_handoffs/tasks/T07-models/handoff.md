# Handoff — T07 Train, tune (on validation only), and evaluate ML models vs. baselines
Worker: worker · Date: 2026-11-09 16:05

## What was done
1. Implemented `src/models/train_models.py` for training, validation-only tuning, and multi-split evaluation of the 3 locked models from SSOT §2:
   - `logistic_regression`: Pipeline of `StandardScaler` + `LogisticRegression(class_weight='balanced')`
   - `random_forest`: `RandomForestClassifier(class_weight='balanced_subsample')`
   - `hist_gradient_boosting`: `HistGradientBoostingClassifier(class_weight='balanced')`
2. Adhered strictly to the time-series anti-leakage rules:
   - Estimators and scalers fit strictly on `train` (1994–2015, 19,632 rows).
   - Hyperparameters tuned on `val` (2016–2017, 1,848 rows) via PR-AUC.
   - Operating probability thresholds calibrated on `val` via $F_2$-score maximization (per R1 Q5 public health priority: recall > precision).
   - `test` (2018–2022, 4,620 rows) and its subperiods evaluated once without refitting.
3. Updated `results/metrics.json` preserving `"dataset"` and `"baselines"`, adding `"features_used"` (25 predictor features), `"best_model_name"` (`hist_gradient_boosting`), and `"models"` with complete confusion matrices, metrics, hyperparameter grids, and feature importances.
4. Exported row-level prediction files for error and cost analysis (T08/T09):
   - `data/processed/val_predictions.csv` (1,848 rows, 0 NaNs)
   - `data/processed/test_predictions.csv` (4,620 rows, 0 NaNs)
5. Generated `results/figures/r4_model_vs_baseline.png` (300 DPI, 290.9 KB publication grouped bar chart for Poster Box R4).
6. Generated `results/modeling_report.md` comparing all 3 baselines and all 3 ML models across all splits and detailing epidemiological feature importance.
7. Created `tests/test_models.py` with 7 unit tests (all 35 project tests pass).

## Files created / changed
- `src/models/train_models.py` (created)
- `results/metrics.json` (updated with `"models"`, `"best_model_name"`, `"features_used"`)
- `data/processed/val_predictions.csv` (created, 1,848 rows)
- `data/processed/test_predictions.csv` (created, 4,620 rows)
- `results/figures/r4_model_vs_baseline.png` (created, 300 DPI)
- `results/modeling_report.md` (created)
- `tests/test_models.py` (created)

## Commands run and real output

### 1. Execute train_models.py pipeline
```
Loading parameters and dataset...
Train split: 19632 rows, Val split: 1848 rows
Tuning Logistic Regression...
  LR best C=0.01, val PR-AUC=0.6745, thr=0.54
Tuning Random Forest...
  RF best params={'max_depth': 10, 'min_samples_leaf': 5, 'n_estimators': 100, 'class_weight': 'balanced_subsample', 'random_state': 42}, val PR-AUC=0.6672, thr=0.45
Tuning HistGradientBoosting...
  HGB best params={'learning_rate': 0.1, 'max_depth': 4, 'min_samples_leaf': 20, 'class_weight': 'balanced', 'random_state': 42}, val PR-AUC=0.6854, thr=0.49
Computing feature importances...
Evaluating models across all splits...
Updated results\metrics.json with models section.
Generating validation and test prediction files...
Saved val_predictions.csv (1848 rows) and test_predictions.csv (4620 rows).
Generating Poster Box R4 figure...
Saved results/figures/r4_model_vs_baseline.png.
Generating modeling report...
Saved results/modeling_report.md.
```

### 2. Print metrics schema across all models and splits
Command:
```powershell
python -c "import json; m=json.load(open('results/metrics.json')); [print(k, s, {x: round(m['models'][k]['metrics'][s][x],4) for x in ['recall','precision','f1','pr_auc']}) for k in m['models'] for s in ['val','test','test_normal_2018_2019','test_covid_2020_2022']]"
```
Real output:
```
logistic_regression val {'recall': 0.8429, 'precision': 0.5043, 'f1': 0.631, 'pr_auc': 0.6745}
logistic_regression test {'recall': 0.8597, 'precision': 0.5892, 'f1': 0.6992, 'pr_auc': 0.7702}
logistic_regression test_normal_2018_2019 {'recall': 0.8587, 'precision': 0.5833, 'f1': 0.6947, 'pr_auc': 0.7764}
logistic_regression test_covid_2020_2022 {'recall': 0.8618, 'precision': 0.6023, 'f1': 0.709, 'pr_auc': 0.7623}
random_forest val {'recall': 0.7714, 'precision': 0.587, 'f1': 0.6667, 'pr_auc': 0.6672}
random_forest test {'recall': 0.8291, 'precision': 0.5898, 'f1': 0.6893, 'pr_auc': 0.7698}
random_forest test_normal_2018_2019 {'recall': 0.8364, 'precision': 0.589, 'f1': 0.6912, 'pr_auc': 0.7751}
random_forest test_covid_2020_2022 {'recall': 0.813, 'precision': 0.5917, 'f1': 0.6849, 'pr_auc': 0.7575}
hist_gradient_boosting val {'recall': 0.8857, 'precision': 0.4627, 'f1': 0.6078, 'pr_auc': 0.6854}
hist_gradient_boosting test {'recall': 0.8827, 'precision': 0.5398, 'f1': 0.6699, 'pr_auc': 0.7657}
hist_gradient_boosting test_normal_2018_2019 {'recall': 0.8922, 'precision': 0.5393, 'f1': 0.6723, 'pr_auc': 0.7762}
hist_gradient_boosting test_covid_2020_2022 {'recall': 0.8618, 'precision': 0.5408, 'f1': 0.6646, 'pr_auc': 0.7491}
```

### 3. Verify prediction files row count and 0 NaNs
Command:
```powershell
python -c "import pandas as pd; v=pd.read_csv('data/processed/val_predictions.csv'); t=pd.read_csv('data/processed/test_predictions.csv'); print(f'val_rows: {len(v)}, val_nans: {v.isna().sum().sum()}'); print(f'test_rows: {len(t)}, test_nans: {t.isna().sum().sum()}')"
```
Real output:
```
val_rows: 1848, val_nans: 0
test_rows: 4620, test_nans: 0
```

### 4. Verify figure size and 300 DPI
Command:
```powershell
python -c "from pathlib import Path; from PIL import Image; p=Path('results/figures/r4_model_vs_baseline.png'); img=Image.open(p); dpi=img.info.get('dpi'); print('exists:', p.exists(), 'size_kb:', round(p.stat().st_size/1024, 2), 'dimensions:', img.size, 'dpi:', dpi)"
```
Real output:
```
exists: True size_kb: 290.92 dimensions: (3785, 2070) dpi: (299.9994, 299.9994)
```

### 5. Run full pytest suite
Command:
```powershell
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
collected 35 items

tests\test_baselines.py ........                                         [ 22%]
tests\test_build_panel.py ....                                           [ 34%]
tests\test_eda.py .....                                                  [ 48%]
tests\test_features_and_leakage.py .....                                 [ 62%]
tests\test_models.py .......                                             [ 82%]
tests\test_province_centroids.py ....                                    [ 94%]
tests\test_weather.py ..                                                 [100%]

============================= 35 passed in 10.26s =============================
```

## Results

### Model vs Baseline Test Set Summary (2018–2022 Overall, 4,620 rows, 392 outbreaks)
| Method | Recall (Primary) | Precision | F1-Score | PR-AUC | TP | FP | FN |
|---|---|---|---|---|---|---|---|
| Majority Class (Baseline 1) | 0.0000 | 0.0000 | 0.0000 | 0.0848 | 0 | 0 | 392 |
| Persistence t-1 (Baseline 2) | 0.6224 | 0.6321 | 0.6272 | 0.4255 | 244 | 142 | 148 |
| Seasonal t-12 (Baseline 3) | 0.2832 | 0.2984 | 0.2906 | 0.1453 | 111 | 261 | 281 |
| Logistic Regression | 0.8597 | 0.5892 | **0.6992** | **0.7702** | 337 | 235 | 55 |
| Random Forest | 0.8291 | **0.5898** | 0.6893 | 0.7698 | 325 | 226 | 67 |
| **HistGradientBoosting** (Best) | **0.8827** | 0.5398 | 0.6699 | 0.7657 | **346** | 295 | **46** |

- **Recall Improvement:** HistGradientBoosting caught **346** out of 392 outbreak months (88.27%), missing only 46 outbreaks nationwide across 5 years, compared to the persistence baseline missing 148 outbreaks (catching only 244, 62.24%). This represents a **+26.0 percentage point gain** in early outbreak detection.
- **Precision Preservation:** Despite high sensitivity, all models maintained precision between 54.0% and 59.0%, and F1 between 0.670 and 0.699 (higher than all baselines).

## Acceptance criteria status
| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `python src/models/train_models.py` runs with exit code 0 | PASS | Runs cleanly in ~45s, exit code 0 |
| 2 | Model metrics print for all models across 4 splits | PASS | Exact dictionary outputs verified |
| 3 | `val_predictions.csv` (1,848) and `test_predictions.csv` (4,620) exist, 0 NaNs | PASS | Confirmed via pandas check |
| 4 | `r4_model_vs_baseline.png` exists (>20 KB, 300 DPI) | PASS | 290.9 KB, 300 DPI, 3785x2070 px |
| 5 | `pytest` passes all tests including `tests/test_models.py` | PASS | 35 passed in 10.26s |

## Deviations from the brief
None.

## UNVERIFIED items
None. All numbers and outputs were verified through executed code.

## SSOT change requests
None. All models, hyperparameter ranges, splits, and seeds conformed directly to SSOT §2.

## Suggested next steps
1. Orchestrator/reviewer review T07 and mark PASS.
2. Proceed to T08 (Evaluation + Error analysis by province and season) using `data/processed/test_predictions.csv`.
