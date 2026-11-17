# Handoff — T10 Assemble self-contained runnable Colab notebook
Worker: worker · Date: 2026-11-09 17:17

## What was done
1. Implemented `src/notebook/build_notebook.py`, a zero-external-dependency generator script that constructs a valid nbformat v4 Jupyter notebook (`notebooks/capstone_dengue.ipynb`), executes all 12 code cells in a shared namespace, captures real stdout, tables, and 7 inline base64 PNG figures, and validates numerical consistency across R1 through R7.
2. Formatted `notebooks/capstone_dengue.ipynb` into 8 clear pedagogical sections matching CRISP-DM R1–R7:
   - **Section 1: Title, SDG 3 Context & R1 Business Understanding (5 Framing Questions):** Title *"เดือนหน้าไข้เลือดออกระบาดไหม?"*, user (สสจ.), prediction timing ($t$ for $t+1$), row definition (province × month), localized target $\mu_p + 1.0\sigma_p$ (train 1993–2015), and metric justification (Recall on Outbreak Months).
   - **Section 2: R2 Data Understanding, Verification & Temporal Split:** Panel loading (27,720 rows, 77 provinces, 1993–2022), data licenses (OpenDengue v1.3.1 + Open-Meteo CC BY 4.0), 78→77 province resolution (`PRACHIN BURI` 1993–2002 + `PHACHINBURI` 2003–2022), 696 missing months across 5 late-created provinces (0 missing in weather), and chronological split table.
   - **Section 3: R3 Exploratory Data Analysis (Key Findings & Inline Visuals):** Monthly seasonality (April temp 28.60°C, May rain onset 189.84 mm, July dengue peak 114.31 cases/province), weather lag correlations (temp leads by 2–3 months, rain leads by 0–1 month), extreme province heterogeneity (49.78x ratio, 11 masked provinces), and COVID-19 anomaly (11.30x drop), rendering 4 inline EDA figures.
   - **Section 4: R2/R4 Feature Engineering & Zero-Leakage Verification:** 25 causal numerical features, target alignment, verifying 26,100 modeling rows with 0 NaNs and automated causality assertions.
   - **Section 5: R4 Modeling — Baselines vs. Machine Learning Models:** 3 baselines vs 3 ML models (`LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier`), validation $F_2$ threshold tuning, full comparative performance table, validation permutation importance, and rendering Figure 5 (`r4_model_vs_baseline.png`) inline.
   - **Section 6: R5 Evaluation & Quantitative Error Analysis:** Onset vs ongoing failure breakdown (Persistence 0% onset recall vs HGB 73.0% onset recall; 87.0% of HGB FNs are 3.35x single-month explosive spikes), FP anatomy (93.56% near-miss / cooldown / $t+2$ early warning vs 6.44% pure false alarm), 9 named case studies, and rendering Figure 6 (`r5_error_analysis.png`) inline.
   - **Section 7: R6 Deployment — Two-Tier Operational Protocol & Cost Sensitivity:** Two-Tier protocol (Green 0.90% risk, Yellow 17.12% risk, Red 60.53% risk; 91.07% recall), cost sensitivity across $R \in \{3, 5, 10, 15\}$ (saving 66–76% cost vs baselines, 72.2% fewer alerts vs Blanket Rainy-Season), dynamic 56.0% workload reduction during COVID-19, 4 operational limitations, and rendering Figure 7 (`r6_threshold_policy.png`) inline.
   - **Section 8: R7 AI-Use Log Summary & Automated Consistency Audit:** AI rejection/correction log table and automated assertion block verifying all computed notebook metrics match `results/*.json` to 4 decimal places.
3. Created `tests/test_notebook.py` containing 7 test cases covering JSON schema validity, zero execution errors, cell counts, required sections, inline PNG figures, and numerical consistency.
4. Added Colab environment portability fallback checking repository presence and directory structure.

## Files created / changed
- `src/notebook/__init__.py` (new)
- `src/notebook/build_notebook.py` (new)
- `notebooks/capstone_dengue.ipynb` (new, 20 cells, 7 inline PNGs, 1.54 MB)
- `tests/test_notebook.py` (new, 7 test functions)

## Commands run and real output
```powershell
# Command 1: Generator script execution
python src/notebook/build_notebook.py
```
Output:
```
Executing and building self-contained notebook: notebooks/capstone_dengue.ipynb...
Successfully generated executed notebook: notebooks\capstone_dengue.ipynb (20 cells)
Build complete.
```

```powershell
# Command 2: JSON schema, cell count, error count, and inline image verification
python -c "import json; nb=json.load(open('notebooks/capstone_dengue.ipynb', encoding='utf-8')); code_cells=[c for c in nb['cells'] if c['cell_type']=='code']; errs=[o for c in code_cells for o in c.get('outputs',[]) if o.get('output_type')=='error']; imgs=[o for c in code_cells for o in c.get('outputs',[]) if 'image/png' in o.get('data',{})]; print('Cells:', len(nb['cells']), 'Code:', len(code_cells), 'Errors:', len(errs), 'Inline PNGs:', len(imgs)); assert len(errs)==0 and len(imgs)>=4"
```
Output:
```
Cells: 20 Code: 12 Errors: 0 Inline PNGs: 7
```

```powershell
# Command 3: Pytest test suite
pytest
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2
collected 65 items

tests\test_baselines.py ........                                         [ 12%]
tests\test_build_panel.py ....                                           [ 18%]
tests\test_eda.py .....                                                  [ 26%]
tests\test_error_analysis.py ........                                    [ 38%]
tests\test_features_and_leakage.py .....                                 [ 46%]
tests\test_models.py .......                                             [ 56%]
tests\test_notebook.py .......                                           [ 67%]
tests\test_province_centroids.py ....                                    [ 73%]
tests\test_recommendations.py ...............                            [ 96%]
tests\test_weather.py ..                                                 [100%]

============================= 65 passed in 13.99s =============================
```

## Results
All figures and metrics in `notebooks/capstone_dengue.ipynb` match `results/*.json` exactly:
- **Test Set 2018–2022 Outbreak Months:** 392 (prevalence: 8.48%)
- **HistGradientBoosting (Operating Threshold = 0.49):**
  - Recall: **0.8827** (346 / 392 outbreaks caught 1 month ahead)
  - Precision: **0.5398** (F1: **0.6699**)
  - PR-AUC: **0.7657**
  - Confusion counts: TP = 346, FP = 295, FN = 46, TN = 3,933
- **Baseline Comparators on Test Set:**
  - Majority Class: Recall = 0.0000, PR-AUC = 0.0848
  - Persistence (t-1): Recall = 0.6173, Precision = 0.5052, F1 = 0.5557, PR-AUC = 0.3444
  - Seasonal (t-12): Recall = 0.2781, Precision = 0.2978, F1 = 0.2876, PR-AUC = 0.1440
- **Onset vs. Ongoing Outbreaks:**
  - Persistence Onset Recall: **0.0%** (0 / 148 caught)
  - HistGradientBoosting Onset Recall: **72.97%** (108 / 148 caught)
  - HGB False Negatives: **86.96%** (40 / 46) are explosive onsets jumping by a mean of **3.35x**
- **False Positive Anatomy:**
  - 93.56% (276 / 295) actionable/near-miss alerts (41.02% near-miss, 36.95% cooldown tail, 15.59% $t+2$ early warning)
  - 6.44% (19 / 295) pure false alarms
- **Two-Tier Protocol:**
  - Green ($P < 0.35$): 3,871 months, 0.90% empirical outbreak risk
  - Yellow ($0.35 \le P < 0.65$): 222 months, 17.12% outbreak risk, 38 outbreaks caught
  - Red ($P \ge 0.65$): 527 months, 60.53% outbreak risk, 319 outbreaks caught
  - Combined alerts ($P \ge 0.35$): 749 alerts, 357 outbreaks caught (**91.07% recall**)

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/notebook/build_notebook.py` exits with code 0 and generates `notebooks/capstone_dengue.ipynb` with all cells executed and outputs populated | PASS | Exit code 0, 20 cells generated, outputs populated |
| 2 | Python verification command asserts `Errors == 0` and `Inline PNGs >= 4` | PASS | `Cells: 20 Code: 12 Errors: 0 Inline PNGs: 7` |
| 3 | `pytest` passes all tests (including `tests/test_notebook.py`) | PASS | 65 passed in 13.99s (7/7 in `test_notebook.py`) |

## Deviations from the brief
None.

## UNVERIFIED items
None. All numbers are computed from code and verified against `results/*.json`.

## SSOT change requests
None.

## Suggested next steps
- Proceed to T11: Poster content drafting in Thai (A2 layout matching R1–R7) and generating QR code pointing to the Colab notebook.
