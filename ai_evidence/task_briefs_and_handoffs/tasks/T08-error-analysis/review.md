# Review — T08 Quantitative error analysis and failure case studies (R5)
Reviewer: reviewer · Date: 2026-11-09

## Verdict
PASS

## Checks run
| Check | Result |
|---|---|
| `python src/models/error_analysis.py` exit code & outputs | PASS (exit code 0; generates `results/error_analysis.json`, `results/figures/r5_error_analysis.png`, `results/error_analysis.md`) |
| `results/error_analysis.json` schema & exact conservation | PASS (392 test outbreaks = 148 onsets + 244 ongoing; HGB catches 108/148 onsets = 73.0% vs Persistence 0/148 = 0.0%; 295 FPs = 121 near-miss + 109 cooldown tail + 46 early warning + 19 pure false alarm) |
| Visual inspection of `results/figures/r5_error_analysis.png` | PASS after reviewer polish (`ylim(0, 145)` in Panel A and `ylim(0, 142)` in Panel D, moving callout boxes to upper right `(0.98, 0.97)` above all bars so zero text/bar overlap remains) |
| `pytest` full test suite (`tests/test_error_analysis.py` + prior suites) | PASS (58 passed) |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| 1 | `src/models/error_analysis.py:597-620, 730-749` | In `r5_error_analysis.png`, Panel A and Panel D callout badges (`y=0.58` in axes coordinates) overlapped the middle bars and bar labels (`62.2%` in Panel A, `68.8%` in Panel D), and Panel A's legend touched `100.0%`. | Fixed directly by reviewer (`ylim` increased to `145` / `142` and callout badges placed in upper-right headroom at `(0.98, 0.97)`). Re-rendered and visually verified. Logged for R7. |

## Hallucination check
- Every claimed file/column/number verified against real output? yes (all 9 named case studies and all partition counts verified directly against `data/processed/test_predictions.csv` and `data/processed/modeling_table.csv`).
- Anything in handoff contradicting SSOT? no.

## Notes for orchestrator
T08 is complete and provides all quantitative findings, tables, case studies, and the 300-DPI 4-panel chart needed for Poster Box R5.
