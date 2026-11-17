# Review — T06 Build and evaluate the 3 baseline classifiers
Reviewer: orchestrator/reviewer · Date: 2026-11-09

## Verdict
PASS

## Checks run
| Check | Result |
|---|---|
| Acceptance check 1: `python src/models/baselines.py` runs to completion | PASS — exited 0 |
| Acceptance check 2: `results/metrics.json` preserves `"dataset"` and populates `"baselines"` for all 3 baselines across all 5 splits | PASS — verified all keys and numbers |
| Acceptance check 3: `results/baselines_report.md` concordance with `results/metrics.json` | PASS — 100% match verified by `test_report_numbers_match_json` |
| Acceptance check 4: Unit tests (`tests/test_baselines.py`) | PASS — 8/8 baseline tests passing |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| — | — | None | — |

## Hallucination check
- Every claimed file/column/number verified against real output? yes
- Anything in handoff contradicting SSOT? no

## Notes for orchestrator
- `T06` is `PASS`. Persistence sets the primary baseline benchmark (`val` recall `0.6000`, `test` recall `0.6224`, `test` F1 `0.6272`).
