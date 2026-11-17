# Review — T07 Train, tune (on validation only), and evaluate ML models vs. baselines
Reviewer: orchestrator/reviewer · Date: 2026-11-09

## Verdict
PASS (after minor reviewer visual-layout adjustment in `src/models/train_models.py` for `r4_model_vs_baseline.png`)

## Checks run
| Check | Result |
|---|---|
| Acceptance check 1: `python src/models/train_models.py` runs to completion | PASS — exited 0 |
| Acceptance check 2: Model metrics in `results/metrics.json` across `val`, `test`, `test_normal_2018_2019`, `test_covid_2020_2022` | PASS — all 3 models beat persistence recall (`0.6224`) by `+20.7` to `+26.0` percentage points on `test` while maintaining precision `0.54–0.59` and F1 `0.67–0.70` |
| Acceptance check 3: `val_predictions.csv` (`1,848` rows) and `test_predictions.csv` (`4,620` rows) completeness | PASS — 0 NaNs |
| Acceptance check 4: Visual inspection of `results/figures/r4_model_vs_baseline.png` (300 DPI) | Caught legend overlapping `0.77` PR-AUC bar labels and top-left callout clipping left spine; adjusted `ylim(0, 1.18)`, `ncol=2` legend, and callout box in `src/models/train_models.py` and re-rendered cleanly |
| Acceptance check 5: Full `pytest` suite (`tests/test_models.py`) | PASS — 35/35 tests passing |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| 1 | `src/models/train_models.py:574-610` | In `r4_model_vs_baseline.png`, the 1-column legend box covered the `0.77` bar labels above the PR-AUC bars, and the Recall callout text clipped the left border. | Fixed directly by reviewer (`ylim(0, 1.18)`, `ncol=2` legend, boxed callout centered at `x=0.0, y=0.95`) and re-rendered; verified visually. |

## Hallucination check
- Every claimed file/column/number verified against real output? yes
- Anything in handoff contradicting SSOT? no

## Notes for orchestrator
- Note for R7 AI-Use Log: The worker also logged a good technical correction in `WORKLOG.md` (`HistGradientBoostingClassifier` does not expose `.feature_importances_`, so validation `permutation_importance` with `scoring='average_precision'` was used instead).
- `T07` is `PASS`. `T08` (Error Analysis, R5) and `T09` (Policy & Cost Recommendations, R6) are next.
