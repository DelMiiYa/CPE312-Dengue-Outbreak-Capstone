# Review — T12 R7 AI-Use Log, Q&A rehearsal guide, and submission readiness check
Reviewer: reviewer · Date: 2026-11-10

## Verdict
PASS

## Checks run
| Check | Result |
|---|---|
| `python src/poster/build_qa_and_r7.py` exit code & outputs | PASS (generates `results/r7_ai_log_and_qa_prep.md` with 7 R7 AI-oversight cases, 3-minute Thai pitch script, 20 bilingual Q&A flashcards, 12-cell notebook walkthrough, team role rotation, and 8-point submission checklist) |
| Numerical check on Q&A flashcards | PASS after reviewer fix (updated Flashcard 13 in `src/poster/build_qa_and_r7.py` to pull `test_normal_2018_2019` recall `85.87%` and `83.64%` for LR and RF instead of overall test recall `85.97%` and `82.91%`) |
| Full repository `pytest` suite (`tests/test_deliverables_ready.py` + all prior suites) | PASS (81 passed in 14.5s) |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| 1 | `src/poster/build_qa_and_r7.py:205-206` | Flashcard 13 ("Recall ยุคปกติ 2018–2019") substituted `{{LR_TEST_RECALL}}` (`85.97%`) and `{{RF_TEST_RECALL}}` (`82.91%`) instead of `test_normal_2018_2019` recall (`85.87%` and `83.64%`). | Fixed directly by reviewer (`{{LR_NORM_RECALL}}` and `{{RF_NORM_RECALL}}`) and regenerated `results/r7_ai_log_and_qa_prep.md`. |

## Hallucination check
- Every claimed file/column/number verified against real output? yes.
- Anything in handoff contradicting SSOT? no.

## Notes for orchestrator
All 12 tasks (`T00`–`T12`) are now PASS.
