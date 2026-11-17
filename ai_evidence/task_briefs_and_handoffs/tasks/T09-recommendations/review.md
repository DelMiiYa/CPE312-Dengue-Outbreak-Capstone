# Review — T09 Cost/threshold trade-off analysis and practical recommendations (R6)
Reviewer: reviewer · Date: 2026-11-09

## Verdict
PASS

## Checks run
| Check | Result |
|---|---|
| `python src/models/recommend_policy.py` exit code & outputs | PASS (exit code 0; generates `results/policy_analysis.json`, `results/figures/r6_threshold_policy.png`, `results/recommendations.md`) |
| `results/policy_analysis.json` schema & calculations | PASS (Two-Tier: Green 3,871 months / 0.90% risk, Yellow 222 months / 17.12% risk, Red 527 months / 60.53% risk; Any Alert = 749 alerts, 357/392 caught = 91.07% recall; Single ML 0.49 catches 346/392 with 72.2% fewer alerts and 85.0% fewer false alarms than Blanket Rainy Season) |
| Visual inspection of `results/figures/r6_threshold_policy.png` | PASS after minor reviewer polish (placed `944` and `1119` labels at `xytext=(0/-6, -15)` below the red Two-Tier curve in Panel B so they never sit between the red and green lines) |
| `pytest` full test suite (`tests/test_recommendations.py` + prior suites) | PASS (58 passed in 10.35s) |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| 1 | `src/models/recommend_policy.py:568` | In Panel B of `r6_threshold_policy.png`, the `1119` annotation at $R=15$ had `xytext=(0, 8)` which placed it between the red Two-Tier line and green Single-Threshold line. | Fixed directly by reviewer (`xytext=(-6 if r_val == 15 else 0, -15)` so all four cost labels sit cleanly below the red curve). Re-rendered and visually verified. |

## Hallucination check
- Every claimed file/column/number verified against real output? yes (all policy comparisons, parametric cost numbers across $R \in \{3, 5, 10, 15\}$, and COVID dynamic alert scaling verified against `results/policy_analysis.json`).
- Anything in handoff contradicting SSOT? no.

## Notes for orchestrator
T09 is complete and provides the Two-Tier Сสจ. decision protocol, cost sensitivity dominance proof, dynamic COVID workload analysis, and 4 observational limitations for Poster Box R6. T10, T11, and T12 can now be briefed and executed.
