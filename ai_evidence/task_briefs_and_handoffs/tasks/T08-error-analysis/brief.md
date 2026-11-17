# Brief — T08 Quantitative error analysis and failure case studies (R5)
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Analyze where and why the primary model (`hist_gradient_boosting`, alongside `logistic_regression` and the `persistence_last_month` baseline) succeeds and fails on the 5-year test set (`2018–2022`, `4,620` rows), save all numbers to `results/error_analysis.json`, generate `results/figures/r5_error_analysis.png` (300 DPI), and write `results/error_analysis.md` for Poster Box **R5**.

## Why
Serves requirement(s): R5 (Know where the model fails — concrete failure patterns and examples with reasons; also a gallery-walk dot-sticker voting category!). Depends on: T07 (PASS).

## Inputs (exact paths)
- `data/processed/test_predictions.csv`
- `data/processed/modeling_table.csv`
- `results/metrics.json`
- `config/params.yaml`

## Outputs (exact paths)
- `src/models/error_analysis.py` — reproducible script computing all error breakdowns, case studies, and plots
- `results/error_analysis.json` — structured JSON with all numbers cited in `results/error_analysis.md`
- `results/figures/r5_error_analysis.png` — 300-DPI multi-panel figure for Poster Box R5 (e.g., Panel A: Recall on Outbreak Onset `outbreak_lag_0 == 0` vs. Ongoing Outbreak `outbreak_lag_0 == 1` comparing Persistence vs. ML models; Panel B: Monthly/Seasonal distribution of False Negatives, False Positives, and True Positives or False Positive breakdown by cause)
- `results/error_analysis.md` — analytical report for Poster Box R5 (every number sourced from `results/error_analysis.json`)
- `tests/test_error_analysis.py` — unit tests verifying JSON schema, arithmetic conservation of TP/FP/TN/FN, figure existence, and markdown concordance

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`.
- Join `data/processed/test_predictions.csv` with `data/processed/modeling_table.csv` on `['province_en', 'year', 'month', 'target_year', 'target_month', 'split', 'subperiod']` so all lag features (`cases_lag_0`, `outbreak_lag_0`, `cases_zscore_lag_0`, `precip_lag_0..3`, `temp_lag_0..3`, `mean_p`, `sd_p`) are available for every test prediction.
- **Quantify at least these 4 failure/performance dimensions in `results/error_analysis.json` and `results/error_analysis.md`:**
  1. **Outbreak Onset vs. Ongoing Continuation (Why FN = 46 happens & where ML beats Persistence):**
     - Partition the `392` test outbreak months (`outbreak_t1 == 1`) into:
       - **Onset months (`outbreak_lag_0 == 0` and `outbreak_t1 == 1`):** First month crossing `threshold_p`. Note that `persistence_last_month` has **0% recall** here by definition! Compute how many onset months exist in `test`, and report Recall, TP, and FN on onset months for `persistence_last_month`, `logistic_regression`, `random_forest`, and `hist_gradient_boosting`.
       - **Ongoing months (`outbreak_lag_0 == 1` and `outbreak_t1 == 1`):** Consecutive outbreak months. Report Recall, TP, and FN for each method.
     - Show what share of `hist_gradient_boosting`'s `46` False Negatives are sudden **Onset months** vs. **Ongoing months**, and compare the average case jump (`target_cases_t1 / max(cases_lag_0, 1)`) and prior Z-score (`cases_zscore_lag_0`) of missed onset months vs. detected onset months.
  2. **Anatomy of the 295 False Positives (`outbreak_t1 == 0` and `pred_hist_gradient_boosting == 1`):**
     - Partition the `295` FPs of `hist_gradient_boosting` into mutually exclusive or overlapping diagnostic categories:
       - **Post-outbreak cool-down / tail months (`outbreak_lag_0 == 1` and `outbreak_t1 == 0`):** Month $t$ was an outbreak, and in month $t+1$ cases dropped below `threshold_p`.
       - **Near-miss / elevated endemic months (`target_cases_t1 >= mean_p` and `target_cases_t1 <= threshold_p`):** Cases in month $t+1$ were genuinely above the province's historical mean (`mean_p`), just short of the `mean_p + 1*SD_p` cutoff (`target_cases_t1 / threshold_p` ratio).
       - **Pre-outbreak early warnings (`outbreak_t1 == 0` at $t+1$, but outbreak occurs at $t+2$):** Alarms that fired 1 month early before a true outbreak!
  3. **Geographic / Burden Tier & Temporal (Normal vs. COVID-19, Seasonality) Breakdown:**
     - Group the 77 provinces into 3 burden tiers by train `mean_p` (Low, Medium, High burden) and report Recall, Precision, F1, FN, and FP per tier.
     - Report error rates by calendar month (`target_month` 1..12) and year (`2018`–`2022`).
  4. **Concrete Named Case Studies (Table of real rows from `test`):**
     - Include a markdown table of:
       - **3 False Negative examples** (sudden onset spikes missed by the model)
       - **3 False Positive examples** (e.g., near-threshold peak-season month or post-outbreak tail month)
       - **3 Early-Onset True Positive wins** (`outbreak_lag_0 == 0` and `outbreak_t1 == 1` where `persistence_last_month` predicted `0` but `hist_gradient_boosting` predicted `1` and caught the outbreak 1 month ahead)
     - For each example, show: `province_en`, `target_year-target_month`, `cases_lag_0` (month $t$), `target_cases_t1` (month $t+1$), `threshold_p`, `prob_hist_gradient_boosting`, and a 1-sentence epidemiological explanation.
- **Visual design constraint for `results/figures/r5_error_analysis.png`:**
  - Keep titles, legends, and bar annotations well-spaced with generous `ylim` padding so no text overlaps any border or legend.

## Out of scope
Retraining models or changing model predictions (`test_predictions.csv` is locked from T07).

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/models/error_analysis.py` runs to completion with exit code 0.
2. `python -c "import json; e=json.load(open('results/error_analysis.json')); print('Keys:', list(e.keys())); print('Onset vs Ongoing HGB:', e['onset_vs_ongoing']['hist_gradient_boosting']); print('FP anatomy HGB:', e['fp_anatomy_hgb'])"`
3. `results/figures/r5_error_analysis.png` exists (> 20 KB, 300 DPI).
4. `pytest` passes all unit tests including `tests/test_error_analysis.py`.
