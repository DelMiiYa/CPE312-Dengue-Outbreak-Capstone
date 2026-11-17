# Brief — T09 Cost/threshold trade-off analysis and practical recommendations (R6)
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Build a quantitative threshold-policy and cost/workload trade-off analysis for Provincial Public Health Offices (สสจ.) to support Poster Box **R6** (`src/models/recommend_policy.py`), save all policy numbers to `results/policy_analysis.json`, generate `results/figures/r6_threshold_policy.png` (300 DPI), and write `results/recommendations.md`.

## Why
Serves requirement(s): R6 (Practical recommendation: what the user should do, cost/trade-off, and limitations the data cannot prove; also a gallery-walk dot-sticker voting category!). Depends on: T08 (PASS).

## Inputs (exact paths)
- `data/processed/val_predictions.csv`
- `data/processed/test_predictions.csv`
- `results/metrics.json`
- `results/error_analysis.json`
- `config/params.yaml`

## Outputs (exact paths)
- `src/models/recommend_policy.py` — reproducible script evaluating alert policies, workload, and relative cost ratios
- `results/policy_analysis.json` — structured JSON with all policy, workload, and cost numbers cited in `results/recommendations.md`
- `results/figures/r6_threshold_policy.png` — 300-DPI 2-panel figure for Poster Box R6 (e.g., Panel A: Recall vs. Precision / Alert Workload curve across probability thresholds `0.20–0.80` on Test with the Two-Tier alert zones shaded; Panel B: Expected Relative Cost or Caught Outbreaks vs. Alert Workload across strategies)
- `results/recommendations.md` — actionable deployment guide, cost/workload table, and limitations section for Poster Box R6
- `tests/test_recommendations.py` — unit tests verifying `results/policy_analysis.json`, figure existence, and numerical consistency

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`.
- **1. Actionable Decision Protocol for สสจ. (Two-Tier Early Warning System at End of Month $t$ for Month $t+1$):**
  Evaluate and compare the following concrete operational policies on `test` (`4,620` province-months = `77` provinces × `60` months, `392` true outbreaks):
  - **No-Alert Baseline (`majority_class`):** 0 alerts, 0% outbreaks caught (`392` missed outbreaks).
  - **Blanket Rainy-Season Campaign (`target_month in [5, 6, 7, 8, 9, 10]`):** Alerts every province 6 months/year (`2,310` alerts = 50% of all province-months). Compute its exact Recall, Precision, FP, FN on `test`!
  - **Reactive Persistence Policy (`persistence_last_month`):** Only acts when month $t$ is already in outbreak (`386` alerts, `62.24%` recall, misses `100%` of outbreak onsets).
  - **Single-Threshold ML Policy (`hist_gradient_boosting` at val-tuned `thr = 0.49`):** `641` total alerts over 5 years (`1.66` alerts/province/year = `13.87%` of province-months), catching `346 / 392` outbreaks (`88.27%` recall, `53.98%` precision).
  - **Two-Tier ML Operational Protocol (`hist_gradient_boosting`):**
    - **Green / Routine (`prob < 0.35`):** Routine surveillance only.
    - **Yellow / Tier-1 Watch (`0.35 <= prob < 0.65`):** Low-cost pre-emptive community larval-source removal (รณรงค์ อสม. กำจัดแหล่งเพาะพันธุ์ลูกน้ำยุงลาย ภาชนะขังน้ำ) and stock check.
    - **Red / Tier-2 High Alert (`prob >= 0.65`):** Intensive vector control (targeted thermal fogging / ULV spraying in high-risk subdistricts) + hospital bed, IV fluid, and platelet surge readiness 1 month ahead.
    - Compute exact counts and outbreak capture rates for Green, Yellow, and Red tiers on both `val` and `test`!
- **2. Explicit Cost & Workload Trade-off Analysis (R6 requirement):**
  - Define normalized intervention cost where 1 standard alert campaign (`FP` or `TP` preventive action) = $1\text{ cost unit}$ ($C_{\text{alert}} = 1$, or $0.3\text{ units}$ for Yellow Tier-1 larval control and $1.0\text{ unit}$ for Red Tier-2 full mobilization), and 1 **unprepared missed outbreak (`FN`)** incurs excess reactive emergency fogging + hospitalization surge cost = $R \text{ cost units}$, evaluated across sensitivity ratios $R \in \{3, 5, 10, 15\}$ (clearly labeled as a parametric sensitivity analysis, never claiming a single invented baht figure without sensitivity bounds).
  - Report in `results/policy_analysis.json` and `results/recommendations.md`:
    - Alerts per province per year (`total_alerts / (77 * 5)`) for each policy
    - Outbreaks caught (`TP`) and missed (`FN`) per year nationwide
    - Total normalized cost under each sensitivity ratio $R \in \{3, 5, 10, 15\}$, demonstrating why ML early warning dominates both reactive persistence and blanket rainy-season campaigns whenever $R \ge 3$.
- **3. Explicit Limitations What the Data Cannot Prove (R6 requirement):**
  Document clearly in `results/recommendations.md`:
  - **Observational data vs. causal treatment effect:** The dataset records historical cases under existing public health practices; it cannot prove the exact percentage case reduction achieved by an intervention without a field trial.
  - **Spatial resolution (`Admin1` province vs. village/subdistrict):** Mosquitoes (*Aedes aegypti*) disperse ~100–400 m; a province-level alert tells the สสจ. *when* to mobilize budgets/supplies, but field teams must target specific subdistricts (ตำบล) using local รง.506 surveillance.
  - **Unobserved viral serotypes (DENV-1..4), herd immunity, and human mobility:** The dataset lacks serotype shift data and mobility metrics, which limits prediction of sudden off-season spikes or pandemic lockdown shifts (2020–2022).
  - **Grid reanalysis weather vs. urban microclimates:** ERA5 centroids smooth localized rainfall extremes.

## Out of scope
Retraining models or editing `SSOT.md`.

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/models/recommend_policy.py` runs to completion with exit code 0.
2. `python -c "import json; p=json.load(open('results/policy_analysis.json')); print('Keys:', list(p.keys())); print('Policies:', list(p['policies_test'].keys())); print('Two-tier test:', p['two_tier_test'])"`
3. `results/figures/r6_threshold_policy.png` exists (> 20 KB, 300 DPI, no overlapping text).
4. `pytest` passes all unit tests including `tests/test_recommendations.py`.
