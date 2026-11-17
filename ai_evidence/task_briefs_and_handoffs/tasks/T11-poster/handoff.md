# Handoff — T11 Poster content in Thai (R1–R7), Thai summary update, and number audit
Worker: worker · Date: 2026-11-10 13:32

## What was done
1. Implemented `src/poster/qrcode_gen.py`, a pure-Python, zero-new-dependency standard QR Code generator (Version 4/5 byte mode, Level L error correction, Galois field GF(256) Reed-Solomon encoding) that generates valid, phone-scannable QR code PNG images verified 100% by OpenCV's `cv2.QRCodeDetector`.
2. Implemented `src/poster/build_poster_content.py`, a reproducible generator script that pulls all quantitative results dynamically from `results/metrics.json`, `results/eda_stats.json`, `results/feature_summary.json`, `results/error_analysis.json`, and `results/policy_analysis.json` with zero hard-coded result numbers:
   - Generated `poster/poster_R1_to_R7_th.md` (17,505 characters) structured cleanly box-by-box: `Poster Header`, `Box R1 (Sensible Problem / 5 Framing Questions)`, `Box R2 (Verifiable Data & Chronological Split)`, `Box R3 (EDA Findings & Seasonality)`, `Box R4 (Model vs. Baseline on Test Set)`, `Box R5 (Error Analysis: Onset vs Ongoing & FP Anatomy)`, `Box R6 (Practical Two-Tier Protocol, Cost Dominance & 4 Limits)`, `Box R7 (AI-Use Log & Human Oversight)`, `Footer & QR Codes`, and `Visual Layout Blueprint` for Canva / Figma / PowerPoint A2.
   - Updated `_agent/docs/SUMMARY_TH.md` (5,644 characters) replacing all previous placeholders with verified final project findings.
   - Generated scannable QR code PNGs: `poster/qr_colab.png`, `poster/qr_opendengue.png`, and `poster/qr_weather.png`.
3. Implemented `tests/test_poster_numbers.py` (9 tests) auditing file existence, mandatory box structure, absence of `TBD` or `UNVERIFIED` placeholders, scannability of QR codes, and 100% numerical consistency against all `results/*.json` artifacts.
4. Verified that the full pytest suite passes with 74/74 passed (0 failures).

## Files created / changed
- `src/poster/__init__.py` (new)
- `src/poster/qrcode_gen.py` (new, 218 lines)
- `src/poster/build_poster_content.py` (new, 501 lines)
- `poster/poster_R1_to_R7_th.md` (new, 17,505 chars)
- `poster/qr_colab.png` (new, 1,577 bytes, scannable QR)
- `poster/qr_opendengue.png` (new, 1,544 bytes, scannable QR)
- `poster/qr_weather.png` (new, 1,651 bytes, scannable QR)
- `_agent/docs/SUMMARY_TH.md` (updated, 5,644 chars)
- `tests/test_poster_numbers.py` (new, 9 test functions)

## Commands run and real output
```powershell
# Command 1: Poster build script execution
python src/poster/build_poster_content.py
```
Output:
```
Loading results artifacts from E:\Antigravity-Projects\DS_capstone\results...
Generating poster content: poster/poster_R1_to_R7_th.md...
  -> Generated E:\Antigravity-Projects\DS_capstone\poster\poster_R1_to_R7_th.md (17505 characters)
Updating project summary: _agent/docs/SUMMARY_TH.md...
  -> Updated E:\Antigravity-Projects\DS_capstone\_agent\docs\SUMMARY_TH.md (5644 characters)
Generating scannable QR code PNGs in poster/...
  -> Generated qr_colab.png (1577 bytes)
  -> Generated qr_opendengue.png (1544 bytes)
  -> Generated qr_weather.png (1651 bytes)
Build completed successfully.
```

```powershell
# Command 2: Pytest targeted test suite for poster numbers and QR scannability
pytest tests/test_poster_numbers.py
```
Output:
```
============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-9.1.1, pluggy-1.7.0
rootdir: E:\Antigravity-Projects\DS_capstone
configfile: pytest.ini
plugins: anyio-4.14.2
collected 9 items

tests\test_poster_numbers.py .........                                   [100%]

============================== 9 passed in 0.39s ==============================
```

```powershell
# Command 3: Full test suite execution across the entire repository
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
collected 74 items

tests\test_baselines.py ........                                         [ 10%]
tests\test_build_panel.py ....                                           [ 16%]
tests\test_eda.py .....                                                  [ 22%]
tests\test_error_analysis.py ........                                    [ 33%]
tests\test_features_and_leakage.py .....                                 [ 40%]
tests\test_models.py .......                                             [ 50%]
tests\test_notebook.py .......                                           [ 59%]
tests\test_poster_numbers.py .........                                   [ 71%]
tests\test_province_centroids.py ....                                    [ 77%]
tests\test_recommendations.py ...............                            [ 97%]
tests\test_weather.py ..                                                 [100%]

============================= 74 passed in 15.79s =============================
```

## Results
- **R1 Framing:** สสจ. decision, prediction end of month $t$ for $t+1$, row = province × month, target = $\mu_p + 1.0\sigma_p$ (Train 1993–2015 only), primary metric = Recall on outbreak months.
- **R2 Data Verification:** 27,720 panel rows, 26,100 modeling rows, PRACHIN BURI/PHACHINBURI resolved, 696 missing months across 5 late-starting provinces accounted for. Train 1994–2015: 19,632; Val 2016–2017: 1,848; Test 2018–2022: 4,620 (Normal: 1,848, Covid: 2,772).
- **R3 EDA:** Temp peak month 4 (28.60°C) leads dengue peak month 7 (114.31 cases/prov) by 2–3 months ($r = 0.3940$); rain onset month 5 (189.84 mm) leads by 0–1 month ($r = 0.2853$); province heterogeneity 49.78x (Bangkok 354.45 vs Nong Bua Lamphu 7.12 cases/mo, 11 provinces never reach national threshold); COVID-19 drop 11.30x (87,866 in 2019 to 7,778 in 2021).
- **R4 Modeling vs Baseline (Test 2018–2022, 392 outbreaks):**
  - Majority Class: Recall 0.0%, F1 0.0000, PR-AUC 0.0848
  - Seasonal Last Year: Recall 28.32%, F1 0.2906, PR-AUC 0.1453
  - Persistence Last Month: Recall 62.24% (244/392), F1 0.6272, PR-AUC 0.4255, FN = 148
  - HistGradientBoosting (thresh 0.49): Recall 88.27% (346/392), Precision 53.98%, F1 0.6699, PR-AUC 0.7657, FN = 46 (+26.03 percentage points recall, -68.9% missed outbreaks; Normal recall 89.22%, Covid recall 86.18%).
- **R5 Error Analysis:**
  - Onset (148) vs Ongoing (244): Persistence onset recall 0.0% vs HGB onset recall 73.0% (108/148).
  - 46 FNs: 87.0% (40/46) are sudden explosive onsets jumping 3.35x in 1 month (Bueng Kan 14.1x, Sing Buri 10.5x, Udon Thani 10.4x).
  - 295 FPs: 93.6% (276/295) actionable/near-miss (elevated near-miss 41.0%, post-outbreak tail 36.9%, $t+2$ early warning 15.6%), pure false alarms only 6.4% (19/295).
- **R6 Two-Tier Protocol & Policy:**
  - Green ($p < 0.35$): 83.8% of months, 0.90% risk.
  - Yellow Watch ($0.35 \le p < 0.65$): 4.8% of months, 17.12% risk (0.58 alerts/prov/yr) -> 0.3x อสม. larval source removal.
  - Red High Alert ($p \ge 0.65$): 11.4% of months, 60.53% risk (1.37 alerts/prov/yr) -> 1.0x EOC, ULV fogging, beds & Ringer's lactate.
  - Overall alert ($p \ge 0.35$): 91.07% recall (357/392 outbreaks).
  - Cost dominance for $R \ge 3$: saves 65.9%–69.7% cost vs blanket rainy-season campaign; cuts alerts by 72.2% and false alarms by 85.0% at threshold 0.49; dynamically reduces alerts by 56.0% during COVID-19.
  - 4 operational limits documented (observational vs causal, Admin1 vs 100–400m vector flight, viral serotypes/immunity, weather stations vs water jars).
- **R7 AI-Use Log:** 5 real correction cases logged (T02 centroid hallucination, T07 missing `feature_importances_`, chart text overlap fixes, data leakage prevention, zero-dependency enforcement).
- **QR Codes:** 3 valid QR PNGs generated and verified scannable via OpenCV.

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/poster/build_poster_content.py` exits with code 0 and generates `poster/poster_R1_to_R7_th.md` and `_agent/docs/SUMMARY_TH.md` | PASS | Exit code 0, generated poster (17,505 chars), updated summary (5,644 chars), generated 3 QR PNGs |
| 2 | `pytest` passes with 0 errors (including `tests/test_poster_numbers.py`) | PASS | 74 passed in 15.79s (9/9 passed in `test_poster_numbers.py`) |

## Deviations from the brief
None. Implemented standalone QR code generation to avoid external dependency violations while strictly ensuring phone-scannable QR PNG images.

## UNVERIFIED items
None. All numbers verified against `results/*.json` via automated tests.

## SSOT change requests
None. All implementations conform to `SSOT.md`.

## Suggested next steps
- Reviewer checks T11.
- Proceed to T12: AI-Use Log consolidation, peer evaluation forms, and gallery walk Q&A rehearsal.
