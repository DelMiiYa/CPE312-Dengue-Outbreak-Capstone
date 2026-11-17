# Brief — T12 R7 AI-Use Log, Q&A rehearsal guide, and submission readiness check
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Generate the comprehensive Gallery Walk Q&A Rehearsal Guide, Complete R7 AI-Use Log, Team Role Rotation Plan, and Final Submission Checklist (`results/r7_ai_log_and_qa_prep.md`) via a reproducible script (`src/poster/build_qa_and_r7.py`) and verify project-wide deliverable completeness with `tests/test_deliverables_ready.py`.

## Why
Serves requirement(s): `R7` (AI-use log), Rubric Criterion 5 (`Teamwork` 5%), Rubric Criterion 6 (`Q&A` 5%), and gallery walk defence preparation where any member may be asked to explain any requirement (`R1`–`R7`) or any cell in `notebooks/capstone_dengue.ipynb`. Depends on: T10, T11.

## Inputs (exact paths)
- `_agent/docs/SSOT.md`
- `_agent/docs/requirements.md`
- `_agent/logs/WORKLOG.md`
- `results/metrics.json`
- `results/eda_stats.json`
- `results/error_analysis.json`
- `results/policy_analysis.json`
- `notebooks/capstone_dengue.ipynb`
- `poster/poster_R1_to_R7_th.md`

## Outputs (exact paths)
- `src/poster/build_qa_and_r7.py` — script that reads `_agent/logs/WORKLOG.md` and `results/*.json` to generate `results/r7_ai_log_and_qa_prep.md`.
- `results/r7_ai_log_and_qa_prep.md` — bilingual (Thai + English) rehearsal and verification manual containing:
  1. **Complete R7 AI-Use Log Table (7 verified cases):** What was asked, what the AI suggested/generated, what was rejected or corrected by verification/human review, why, and the impact on reliability (covering: (a) Rejecting random K-fold split in favor of strict temporal split, (b) Rejecting a single national case threshold in favor of train-only per-province $\mu_p + 1.0\sigma_p$ after proving 11 provinces would never alert, (c) Rejecting Accuracy/ROC-AUC as primary metric in favor of Recall on Outbreak Months + $F_2$ threshold tuning, (d) Catching and fixing the T02 LAEA/shapely centroid documentation hallucination against actual `provinces.geojson` properties, (e) Catching and fixing `HistGradientBoostingClassifier` missing `.feature_importances_` by implementing validation `permutation_importance`, (f) Catching and fixing annotation/legend overlaps on R3, R4, R5, and R6 figures via visual inspection, and (g) Fixing matplotlib `\ge` mathtext parser error to `\geq` in T09).
  2. **3-Minute Gallery Walk Pitch Script (in Thai):** A crisp, natural 3-minute walkthrough from R1 to R7 that any member can deliver when the instructor or peers visit the poster, pointing to the exact charts and numbers.
  3. **20 High-Probability Instructor Q&A Flashcards (Thai & English with exact code/number citations):**
     - R1 questions (Why 1-month lead time? Why $\mu_p + 1.0\sigma_p$? Why Recall instead of Precision or F1? How was the threshold `0.49` chosen without test leakage?)
     - R2 questions (How did you resolve 78 vs 77 provinces? Why not impute the 696 missing months before province creation? How did you prevent future data leakage in rolling means and thresholds?)
     - R3 questions (Why does temperature lead dengue by 2–3 months while rainfall leads by 0–1 month? What happened during COVID-19 in 2020–2022?)
     - R4 questions (Why does Persistence get `62.2%` overall recall but `0.0%` on outbreak onsets? Why did you pick `HistGradientBoosting` over `LogisticRegression` when LR had slightly higher test PR-AUC `0.7702` vs `0.7657`? Answer: Model selection was locked strictly on **Validation Recall** `0.8857` vs `0.8429` and Validation PR-AUC `0.6854` vs `0.6745` before touching Test!)
     - R5 questions (Where does your model fail? Give a real province-month example of a False Negative and a False Positive. Why are `93.6%` of False Positives still useful to สสจ.?)
     - R6 questions (How does the Two-Tier Green/Yellow/Red policy work in practice? How did you calculate cost without inventing Baht numbers? What are the 4 things your data cannot prove?)
     - Notebook Code Walkthrough guide (mapping each notebook cell to the 1-sentence explanation of what the pandas/sklearn code is doing).
  4. **Team Role Division, Gallery Walk Rotation Schedule & Final Submission Checklist** (verifying all items in `_agent/docs/requirements.md`).
- `tests/test_deliverables_ready.py` — final end-to-end verification test checking that all project deliverables (data files, 6 figures at 300 DPI, JSON artifacts, executed Colab notebook, Thai poster markdown, Thai summary, and Q&A/R7 guide) exist and are internally consistent.

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`. Do **not** edit `_agent/docs/SSOT.md`.
- Every number cited in the Q&A answers and 3-minute pitch must be pulled dynamically from `results/*.json`.

## Out of scope
- Do not modify any upstream modeling or evaluation scripts.

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/poster/build_qa_and_r7.py` → exits with code `0` and generates `results/r7_ai_log_and_qa_prep.md`.
2. `pytest` → all tests across the entire repository (including `tests/test_deliverables_ready.py`) pass with 0 errors.

## Known pitfalls
- Always use `encoding="utf-8"` when reading and writing markdown/JSON files on Windows.
