# Brief — T10 Assemble self-contained runnable Colab notebook
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Build a self-contained, top-to-bottom runnable Jupyter/Colab notebook (`notebooks/capstone_dengue.ipynb`) via a reproducible generator script (`src/notebook/build_notebook.py`) that executes all cells, embeds real outputs and inline figures, and verifies that every number in the notebook matches `results/metrics.json`, `results/eda_stats.json`, `results/error_analysis.json`, and `results/policy_analysis.json`.

## Why
Serves requirement(s): Course deliverable (`runnable Colab notebook`, worth 30% under Rubric Criterion 2 + Q&A inspection, where every number on the poster must match the notebook). Depends on: T01–T09.

## Inputs (exact paths)
- `_agent/docs/SSOT.md` (locked definitions, splits, features, metrics)
- `_agent/docs/requirements.md` (course rubric and R1–R7 requirements)
- `config/params.yaml`
- `data/processed/panel.csv`
- `data/processed/province_thresholds.csv`
- `data/processed/modeling_table.csv`
- `results/eda_stats.json`
- `results/feature_summary.json`
- `results/metrics.json`
- `results/error_analysis.json`
- `results/policy_analysis.json`
- Existing pipeline scripts (`src/data/build_panel.py`, `src/eda/run_eda.py`, `src/features/build_features.py`, `src/models/baselines.py`, `src/models/train_models.py`, `src/models/error_analysis.py`, `src/models/recommend_policy.py`)

## Outputs (exact paths)
- `src/notebook/build_notebook.py` — script that constructs `notebooks/capstone_dengue.ipynb` (valid nbformat v4 JSON), executes every code cell in order, captures real stdout / tables / inline base64 PNG plots into each cell's `outputs` array, and saves the executed `.ipynb`.
- `notebooks/capstone_dengue.ipynb` — the executed, self-contained Colab notebook with Markdown explanations and executed code cells covering R1 through R7.
- `tests/test_notebook.py` — pytest suite verifying that `notebooks/capstone_dengue.ipynb` is valid JSON (nbformat v4), has zero cell execution errors, contains all required R1–R7 sections and inline image outputs, and reproduces the exact metrics in `results/metrics.json`.

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`. Do **not** edit `_agent/docs/SSOT.md`.
- **Self-contained code for Q&A:** During the gallery walk, the instructor will ask random group members to explain specific notebook cells. Therefore, the notebook code cells must **not** just be one-line wrappers like `!python src/models/train_models.py`. Instead, each section must show the actual, readable pandas / scikit-learn / matplotlib logic (loading data, computing train-only thresholds $\mu_p + 1.0\sigma_p$, building lagged features, evaluating the 3 baselines, fitting/evaluating `LogisticRegression`, `RandomForestClassifier`, and `HistGradientBoostingClassifier`, decomposing onset vs. ongoing errors and FP anatomy, and evaluating the Two-Tier policy & cost curves) with clear English comments so any student can read and explain every line!
- **Colab portability:** Include a setup cell at the top that checks if `data/processed/panel.csv` exists locally; if running in a fresh Google Colab session without local files, it provides instructions/automatic fallback to clone or download the processed panel CSV (or build from OpenDengue + cached weather CSVs).
- **Structure of `notebooks/capstone_dengue.ipynb` (8 clear sections matching CRISP-DM R1–R7):**
  1. **Title, SDG 3 Context & R1 Business Understanding (5 Framing Questions):** Project title *"เดือนหน้าไข้เลือดออกระบาดไหม?"* (*Will dengue break out next month?*), user (`สสจ.`), prediction time (end of month $t$ predicting month $t+1$), row definition (`province × month`), target definition (`cases(p, t+1) > mean_p + 1.0 * SD_p` fit on train `1993–2015`), and why **Recall on Outbreak Months (Class 1)** is the primary metric (missed outbreak FN $\gg$ false alarm FP).
  2. **R2 Data Understanding, Verification & Temporal Split:** Load `data/processed/panel.csv` (`27,720` rows = 77 provinces × 360 months, `1993–2022`), show data sources & `CC BY 4.0` licenses (`OpenDengue v1.3` + `Open-Meteo ERA5`), demonstrate the 78→77 province resolution (`PRACHIN BURI` + `PHACHINBURI`), inspect the 696 missing months across 5 newly created provinces, and verify the chronological split (`Train 1994–2015: 19,632 rows`, `Val 2016–2017: 1,848 rows`, `Test 2018–2022: 4,620 rows` split into `Normal 2018–2019` and `COVID 2020–2022`).
  3. **R3 Exploratory Data Analysis (Key Findings & Inline Visuals):** Compute and display train-only seasonal peaks (April temp `28.60°C`, May rain onset `189.84 mm`, July dengue peak `114.31` cases), cross-correlation lags (Temp leads by 2–3 months, Rain leads by 0–1 month), province heterogeneity (`49.78x` ratio between Bangkok and Nong Bua Lamphu; `11` provinces never alerting under a national cutoff), and the `11.30x` COVID-19 drop (`2019` vs `2021`), rendering inline charts.
  4. **R2/R4 Feature Engineering & Zero-Leakage Verification:** Show how the 25 causal features (case lags, rolling stats, province-normalized z-score, weather lags, anomalies, interaction, cyclical calendar, static baseline) and `outbreak_t1` target are constructed without future leakage, and verify `data/processed/modeling_table.csv` (`26,100` rows, `0` NaNs).
  5. **R4 Modeling — Baselines vs. Machine Learning Models:** Run and compare the 3 baselines (`majority_class`, `persistence_last_month`, `seasonal_last_year`) against the 3 ML models (`logistic_regression`, `random_forest`, `hist_gradient_boosting` with validation $F_2$-tuned thresholds), print the full comparison table on Validation and Test sets (and Normal vs. COVID subperiods), show validation permutation importance, and render the R4 comparison chart inline.
  6. **R5 Evaluation & Quantitative Error Analysis:** Decompose the `392` test outbreaks into `148` Onsets vs. `244` Ongoing continuations (showing Persistence has `0.0%` Onset Recall while `HistGradientBoosting` achieves `73.0%` Onset Recall, and `87.0%` of HGB's `46` FNs are explosive `3.35x` single-month surges), break down the `295` False Positives (`93.6%` near-miss / cooldown tail / $t+2$ early warning vs. only `6.4%` pure false alarms), display the 9 named province-month case studies, and render the R5 error analysis chart inline.
  7. **R6 Deployment — Two-Tier Operational Protocol, Cost Sensitivity & Limitations:** Evaluate the Two-Tier Сสจ. decision protocol (`Green < 0.35` at `0.90%` risk, `Yellow 0.35–0.65` at `17.12%` risk, `Red >= 0.65` at `60.53%` risk; `91.07%` combined recall), compare against Blanket Rainy-Season (`72.2%` fewer alerts and `85.0%` fewer false alarms at `0.49`) and Reactive Persistence across cost ratios $R \in \{3, 5, 10, 15\}$, show dynamic `56.0%` alert scaling during COVID-19, render the R6 two-panel chart inline, and state the 4 observational limitations.
  8. **R7 AI-Use Log Summary & Automated Consistency Audit:** Present the summary table of AI rejections/corrections and run an assertion block verifying that the notebook's computed numbers match `results/metrics.json`, `results/eda_stats.json`, `results/error_analysis.json`, and `results/policy_analysis.json`.

## Out of scope
- Do not modify any numbers in `results/*.json` or `data/processed/*.csv`.

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/notebook/build_notebook.py` → exits with code `0` and generates `notebooks/capstone_dengue.ipynb` with all cells executed and outputs populated.
2. `python -c "import json; nb=json.load(open('notebooks/capstone_dengue.ipynb', encoding='utf-8')); code_cells=[c for c in nb['cells'] if c['cell_type']=='code']; errs=[o for c in code_cells for o in c.get('outputs',[]) if o.get('output_type')=='error']; imgs=[o for c in code_cells for o in c.get('outputs',[]) if 'image/png' in o.get('data',{})]; print('Cells:', len(nb['cells']), 'Code:', len(code_cells), 'Errors:', len(errs), 'Inline PNGs:', len(imgs)); assert len(errs)==0 and len(imgs)>=4"` → prints cell counts, `Errors: 0`, and at least 4 inline PNGs.
3. `pytest` → all tests (including `tests/test_notebook.py`) pass.

## Known pitfalls
- Since `nbformat` or `jupyter` may or may not be installed, check first or build the standard Jupyter Notebook v4 JSON dictionary directly in Python (`{"cells": [...], "metadata": {...}, "nbformat": 4, "nbformat_minor": 5}`) and execute each code cell's source string in a shared namespace using `exec(...)` with `contextlib.redirect_stdout` + matplotlib `BytesIO` -> base64 PNG capture! That approach requires **zero external Jupyter dependencies**, executes in <15 seconds, captures real stdout and inline PNGs into standard `.ipynb` `stream` and `display_data` outputs, and is 100% compatible with Google Colab, VS Code, and GitHub!
