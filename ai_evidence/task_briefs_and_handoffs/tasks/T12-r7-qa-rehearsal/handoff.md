# Handoff — T12 R7 AI-Use Log, Q&A rehearsal guide, and submission readiness check
Worker: worker · Date: 2026-11-10 13:48

## What was done
1. **Implemented Reproducible Guide Generator (`src/poster/build_qa_and_r7.py`):**
   - Ingests quantitative outputs dynamically from `results/metrics.json`, `results/eda_stats.json`, `results/error_analysis.json`, and `results/policy_analysis.json`.
   - Generates bilingual (Thai + English) defense manual `results/r7_ai_log_and_qa_prep.md` (73.4 KB, 316 lines).
   - Zero hardcoded numbers; dynamically formats all metrics, rates, and comparisons.
2. **Complete R7 AI-Use Log Table (7 Verified Cases):**
   - Formatted comprehensive oversight table documenting prompt, AI output, flaw detected by human review, correction made, and reliability impact for all 7 cases:
     (a) Rejecting random K-fold split in favor of strict temporal split (Train 1993–2015, Val 2016–2017, Test 2018–2022) to eliminate look-ahead leakage.
     (b) Rejecting single national threshold in favor of train-only per-province $\mu_p + 1.0\sigma_p$ after proving 11 provinces would never alert (Bangkok 354.4 vs Nong Bua Lamphu 7.1).
     (c) Rejecting Accuracy/ROC-AUC in favor of Recall on Outbreak Months + $F_2$ threshold tuning on Validation.
     (d) Catching and fixing T02 LAEA/shapely centroid documentation hallucination against actual `provinces.geojson` properties.
     (e) Catching and fixing `HistGradientBoostingClassifier` missing `.feature_importances_` by implementing validation `permutation_importance`.
     (f) Catching and fixing annotation/legend overlaps on R3, R4, R5, and R6 figures via visual inspection.
     (g) Fixing matplotlib `\ge` mathtext parser error to `\geq` in T09.
3. **3-Minute Gallery Walk Pitch Script (Thai):**
   - Natural, professional 3-minute delivery script timed in 30-second blocks (0:00 to 3:00) linking problem framing, data, EDA, modeling, error analysis, policy, and AI oversight.
4. **20 High-Probability Instructor Q&A Flashcards:**
   - Bilingual (Thai explanation + English citation) flashcards with exact code references and numbers covering R1 (Cards 1–4), R2 (Cards 5–7), R3 (Cards 8–10), R4 (Cards 11–13), R5 (Cards 14–16), R6 (Cards 17–19), and Notebook 12-cell code walkthrough (Card 20).
5. **Team Role Distribution & Gallery Walk Schedule:**
   - Member 1 (Data Engineer / Custodian), Member 2 (ML Engineer / Modeler), Member 3 (Storyteller & QA Lead).
   - 2-round 30-minute rotation schedule with mid-session transition and instructor defense drill.
   - 8-point final submission readiness checklist.
6. **Created Deliverables Readiness Test Suite (`tests/test_deliverables_ready.py`):**
   - 7 test functions auditing processed data, 6 publication figures (300 DPI, >250KB), 5 JSON artifacts, notebook execution (0 errors, >=4 inline PNGs), poster markdown & scannable QR codes, Q&A/R7 guide integrity (0 unreplaced placeholders), and cross-deliverable numerical consistency.

## Files created / changed
- `src/poster/build_qa_and_r7.py` (created generator script)
- `results/r7_ai_log_and_qa_prep.md` (generated 73.4 KB defense manual)
- `tests/test_deliverables_ready.py` (created 7 automated tests)
- `_agent/tasks/INDEX.md` (updated T12 status)
- `_agent/logs/WORKLOG.md` (logged T12 completion)
- `_agent/tasks/T12-r7-qa-rehearsal/handoff.md` (this file)

## Commands run and real output

### 1. Generator execution: `python src/poster/build_qa_and_r7.py`
```
Generating comprehensive Q&A and R7 guide: E:\Antigravity-Projects\DS_capstone\results\r7_ai_log_and_qa_prep.md...
Successfully generated E:\Antigravity-Projects\DS_capstone\results\r7_ai_log_and_qa_prep.md (73.4 KB)
```

### 2. Deliverables readiness test: `pytest tests/test_deliverables_ready.py`
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
plugins: anyio-4.14.2
collected 7 items

tests\test_deliverables_ready.py .......                                 [100%]

============================== 7 passed in 5.56s ==============================
```

### 3. Full project test suite: `pytest`
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2
collected 81 items

tests\test_baselines.py ........                                         [  9%]
tests\test_build_panel.py ....                                           [ 14%]
tests\test_deliverables_ready.py .......                                 [ 23%]
tests\test_eda.py .....                                                  [ 29%]
tests\test_error_analysis.py ........                                    [ 39%]
tests\test_features_and_leakage.py .....                                 [ 45%]
tests\test_models.py .......                                             [ 54%]
tests\test_notebook.py .......                                           [ 62%]
tests\test_poster_numbers.py .........                                   [ 74%]
tests\test_province_centroids.py ....                                    [ 79%]
tests\test_recommendations.py ...............                            [ 97%]
tests\test_weather.py ..                                                 [100%]

============================= 81 passed in 22.91s =============================
```

## Results
- **HGB Test Recall:** `88.27%` (346 / 392 outbreaks detected)
- **Recall Gain over Persistence Baseline:** `+26.02` percentage points (`88.27%` vs `62.24%`)
- **Missed Outbreaks (FN) Reduction:** `68.9%` reduction (from `148` down to `46` FN)
- **Onset Outbreak Recall:** HGB `73.0%` (108/148) vs Persistence `0.0%` (0/148)
- **False Positive Actionability:** `93.6%` (276/295) are near-misses, tails, or 2-month early warnings; only `6.4%` (19/295) pure false alarms.
- **Two-Tier Early Warning Recall:** `91.07%` (357/392 outbreaks caught in Yellow + Red tiers)
- **Total Repository Pytest Suite:** 81 tests passing with 0 failures across all 12 modules.

## Acceptance criteria status
| # | Criterion | Result | Evidence |
|---|---|:---:|---|
| 1 | `python src/poster/build_qa_and_r7.py` exits code `0` and generates `results/r7_ai_log_and_qa_prep.md` | PASS | Exited code 0, generated 73.4 KB file with 7 verified cases, 3-min pitch, 20 flashcards, 12-cell code walkthrough, and team rotation. |
| 2 | `pytest` passes with 0 errors across entire repository (including `tests/test_deliverables_ready.py`) | PASS | 81 passed in 22.91s with 0 failures, 0 warnings. |

## Deviations from the brief
None. All outputs, sections, and criteria strictly implemented.

## UNVERIFIED items
None. Every metric is verified against `results/*.json` and `notebooks/capstone_dengue.ipynb`.

## SSOT change requests
None.

## Suggested next steps
Reviewer review T10, T11, T12. All 12 project tasks (T01–T12) are now complete and fully verified.
