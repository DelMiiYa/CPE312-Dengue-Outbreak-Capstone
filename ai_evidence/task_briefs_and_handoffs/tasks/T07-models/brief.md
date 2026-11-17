# Brief — T07 Train, tune (on validation only), and evaluate ML models vs. baselines
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Train and tune the ML classification models from SSOT §2 (`LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`) using `train` (`1994–2015`) and `val` (`2016–2017`) only, evaluate once on `test` (`2018–2022` and its normal/COVID subperiods), update `results/metrics.json`, save row-level predictions for error/cost analysis, and generate the Poster Box R4 comparison chart.

## Why
Serves requirement(s): R4 (Model vs. baseline comparison + visualization). Depends on: T05 (PASS), T06 (PASS).

## Inputs (exact paths)
- `data/processed/modeling_table.csv`
- `config/params.yaml`
- `results/metrics.json` (containing `"dataset"` and `"baselines"`)

## Outputs (exact paths)
- `src/models/train_models.py` — reproducible model training, validation tuning, and evaluation pipeline
- `results/metrics.json` — updated with `"models"` section (preserving `"dataset"` and `"baselines"`) and `"best_model_name"`
- `results/modeling_report.md` — full comparison table of all 3 baselines and all trained models across `val`, `test`, `test_normal_2018_2019`, and `test_covid_2020_2022`, plus feature importance summary
- `results/figures/r4_model_vs_baseline.png` — 300-DPI grouped bar chart comparing the 3 baselines vs. the ML models on Recall (primary), Precision, F1, and PR-AUC (for Poster Box R4)
- `data/processed/val_predictions.csv` and `data/processed/test_predictions.csv` — row-level predictions (ID columns + `target_cases_t1`, `threshold_p`, `outbreak_t1` + baseline predictions + `prob_<model>` and `pred_<model>` for each trained model) to feed T08 and T09
- `tests/test_models.py` — unit tests verifying train-only fitting, validation-only tuning, prediction file completeness, and metric consistency

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`.
- **Feature matrix (`X`):** Use the 25 numerical/engineered predictor columns from `modeling_table.csv`:
  `cases_lag_0, cases_lag_1, cases_lag_2, cases_lag_3, cases_roll_mean_3, cases_zscore_lag_0, outbreak_lag_0, outbreak_same_month_last_year, temp_lag_0, temp_lag_1, temp_lag_2, temp_lag_3, precip_lag_0, precip_lag_1, precip_lag_2, precip_lag_3, humidity_lag_0, humidity_lag_1, humidity_lag_2, humidity_lag_3, sin_target_month, cos_target_month, mean_p, sd_p, threshold_p` (or include `month`, `target_month` if desired; record the exact list in `results/metrics.json`). **Never include `target_cases_t1`, `outbreak_t1`, `target_year`, `year`, `split`, or `subperiod` in `X`!**
- **Strict time-series / anti-leakage rule:**
  - Fit `StandardScaler` (for Logistic Regression) and all estimators **strictly on `split == 'train'`** (`19,632` rows).
  - Select hyperparameters and operating probability threshold **strictly on `split == 'val'`** (`1,848` rows). Never look at `test` when choosing hyperparameters or thresholds!
  - Because missed outbreaks (FN) cost more than false alarms (FP) per R1 Q5, train classifiers with `class_weight='balanced'` (`random_state=42`). On `val`, evaluate both the default `0.50` probability cutoff and validation-tuned cutoffs (e.g. searching `thr in np.linspace(0.20, 0.80, 61)` on `val` to maximize $F_2$-score or maximize $F_1$ subject to `val_recall >= persistence_baseline_val_recall` and `val_precision >= 0.5 * persistence_baseline_val_precision` so the model achieves high recall without collapsing precision). Lock the chosen cutoff per model using `val` only, and record both `threshold_used` and the validation tuning rule in `results/metrics.json`.
- **Models to train (`seed = 42` from `config/params.yaml`):**
  1. `logistic_regression`: `Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42, C=...))])` (tune `C` over e.g. `[0.01, 0.1, 1.0, 10.0]` on `val`).
  2. `random_forest`: `RandomForestClassifier(class_weight='balanced_subsample', random_state=42, n_jobs=-1, ...)` (tune `n_estimators`, `max_depth`, `min_samples_leaf` over a compact grid on `val`).
  3. `hist_gradient_boosting`: `HistGradientBoostingClassifier(class_weight='balanced', random_state=42, ...)` (tune `max_depth`, `learning_rate`, `min_samples_leaf` over a compact grid on `val`).
- **Metrics required for each model across `train`, `val`, `test`, `test_normal_2018_2019`, `test_covid_2020_2022`:**
  - Same exact schema as T06 (`recall`, `precision`, `f1`, `pr_auc`, `specificity`, `accuracy`, `tp`, `fp`, `tn`, `fn`, `support_pos`, `support_total`), where `pr_auc` uses the continuous predicted probability `predict_proba(X)[:, 1]`.

## Out of scope
Detailed error breakdown by province/month (covered in T08) and cost/policy analysis (covered in T09).

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/models/train_models.py` runs to completion with exit code 0.
2. `python -c "import json; m=json.load(open('results/metrics.json')); [print(k, s, {x: round(m['models'][k]['metrics'][s][x],4) for x in ['recall','precision','f1','pr_auc']}) for k in m['models'] for s in ['val','test','test_normal_2018_2019','test_covid_2020_2022']]"`
3. `data/processed/val_predictions.csv` (`1,848` rows) and `data/processed/test_predictions.csv` (`4,620` rows) exist with 0 NaNs.
4. `results/figures/r4_model_vs_baseline.png` exists (> 20 KB, 300 DPI, no overlapping text).
5. `pytest` passes all unit tests including `tests/test_models.py`.

## Known pitfalls
- Do not refit on `train + val` before evaluating on `test` if your threshold and `mean_p`/`sd_p` were calibrated on `train` vs `val`—keep the model fitted on `train` (with hyperparameters and threshold selected on `val`) so `val` and `test` predictions come from the exact same fitted model and scaler!
