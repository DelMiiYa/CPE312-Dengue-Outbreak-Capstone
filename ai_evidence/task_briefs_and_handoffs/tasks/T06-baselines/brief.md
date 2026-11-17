# Brief — T06 Build and evaluate the 3 baseline classifiers
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Implement and evaluate the 3 locked baseline classifiers from SSOT §2 across `val` (`2016–2017`), `test` overall (`2018–2022`), `test_normal_2018_2019`, and `test_covid_2020_2022`, and record all metrics in `results/metrics.json` and `results/baselines_report.md`.

## Why
Serves requirement(s): R4 (Model vs. simple baseline using the R1 metric). Depends on: T05 (PASS).

## Inputs (exact paths)
- `data/processed/modeling_table.csv`
- `config/params.yaml`
- `results/metrics.json`

## Outputs (exact paths)
- `src/models/__init__.py`
- `src/models/baselines.py` — idempotent script evaluating the 3 baselines and updating `results/metrics.json`
- `results/metrics.json` — updated with a `"baselines"` top-level key (preserving existing `"dataset"` key)
- `results/baselines_report.md` — clean markdown comparison table generated strictly from `results/metrics.json`
- `tests/test_baselines.py` — unit tests for baseline logic and metric calculations

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`.
- **The 3 locked baselines (SSOT §2):**
  1. `majority_class`: always predicts `0` (non-outbreak, the majority class in `train` where positive rate is `0.097952`). Use constant `y_score = train_pos_rate` for `pr_auc`.
  2. `persistence_last_month`: predicts `y_pred = outbreak_lag_0` (next month $t+1$ has the same outbreak flag as current month $t$). For `pr_auc`, compute `average_precision_score(y_true, outbreak_lag_0)` (and also store `pr_auc_continuous_zscore` using `cases_zscore_lag_0` as an auxiliary field so both binary-flag and continuous persistence rankings are documented).
  3. `seasonal_last_year`: predicts `y_pred = outbreak_same_month_last_year` (outbreak flag of the same calendar month 12 months earlier, $t-11$). For `pr_auc`, compute `average_precision_score(y_true, outbreak_same_month_last_year)`.
- **Evaluation splits to report for every baseline:**
  - `train` (`target_year` 1994–2015, `19,632` rows)
  - `val` (`target_year` 2016–2017, `1,848` rows)
  - `test` (`target_year` 2018–2022, `4,620` rows)
  - `test_normal_2018_2019` (`subperiod == 'normal'`, `1,848` rows)
  - `test_covid_2020_2022` (`subperiod == 'covid'`, `2,772` rows)
- **Metrics required for each (baseline, split) pair:**
  - `recall` (primary R1 metric, `sklearn.metrics.recall_score`, `zero_division=0`)
  - `precision` (`sklearn.metrics.precision_score`, `zero_division=0`)
  - `f1` (`sklearn.metrics.f1_score`, `zero_division=0`)
  - `pr_auc` (`sklearn.metrics.average_precision_score`)
  - `specificity` ($TN / (TN + FP)$)
  - `accuracy` (`sklearn.metrics.accuracy_score`)
  - Confusion matrix integers: `tp`, `fp`, `tn`, `fn`, `support_pos`, `support_total`

## Out of scope
Training ML models (covered in T07).

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/models/baselines.py` runs to completion with exit code 0.
2. `python -c "import json; m=json.load(open('results/metrics.json')); print('Keys:', list(m.keys())); print('Baselines:', list(m['baselines'].keys())); [print(b, s, {k: round(v,4) if isinstance(v,float) else v for k,v in m['baselines'][b][s].items() if k in ['recall','precision','f1','pr_auc','tp','fp','fn']}) for b in m['baselines'] for s in ['val','test','test_normal_2018_2019','test_covid_2020_2022']]"`
3. Every number in `results/baselines_report.md` matches `results/metrics.json` exactly.
4. `pytest` passes all unit tests including `tests/test_baselines.py`.

## Known pitfalls
- Do not overwrite the `"dataset"` key already inside `results/metrics.json`—load the existing JSON, set `metrics["baselines"] = ...`, and write back with `indent=2`.
