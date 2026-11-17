# SSOT — Single Source of Truth
Only the orchestrator edits this file. Every change gets a dated entry in the Changelog.
Tags: `VERIFIED (date, how)` = checked by running code. `UNVERIFIED` = not yet checked, do not rely on it.

## 1. Project statement (R1 five answers)
1. **User / decision:** A provincial public health office (สสจ.) decides whether to start larval-source removal campaigns and prepare hospital resources one month ahead.
2. **Prediction time:** End of month *t*; predict the outbreak flag for month *t+1*. Only data up to and including month *t* may be used. No future weather.
3. **One row:** province × month.
4. **Target:** `outbreak(p, t+1) = 1` if `cases(p, t+1) > mean_p + k·SD_p`, where `mean_p`, `SD_p` are computed per province from **train years only**, `k = 1`.
5. **Costly error:** A missed outbreak (false negative) costs more than a false alarm: late response, preventable cases. Therefore main metric = **recall on outbreak months**, reported with precision, F1, PR-AUC.

Poster title (Thai): **เดือนหน้าไข้เลือดออกระบาดไหม?**
Project name (Thai, form): พยากรณ์เดือนที่เกิดการระบาดของโรคไข้เลือดออกรายจังหวัดในประเทศไทยล่วงหน้า 1 เดือน

## 2. Locked decisions
| Item | Value |
|---|---|
| Task type | Binary classification |
| Row unit | province × month |
| Horizon | 1 month ahead |
| Split (by time) | Train 1993–2015, Validation 2016–2017, Test 2018–2022 |
| Test reporting | Overall; 2018–2019 (normal); 2020–2022 (COVID-affected) |
| Baselines | (a) majority class, (b) outbreak flag same as this month, (c) flag of the same calendar month last year |
| Models | Logistic regression; RandomForest / HistGradientBoosting (sklearn) |
| Tuning | On validation only. Test set evaluated once, at the end |
| Main metric | Recall on outbreak months (class 1) |
| Features | Cases lag 1–3 months, rolling 3-month mean cases, rain and temperature lag 0–3 months, month of year |
| Seed | 42 |

Class balance, early-year data quality, and the 78th province name are unknown until T03/T04. Defaults may change via the Changelog.

## 3. Data facts
### Dengue cases — OpenDengue V1.3.1
- Source: https://opendengue.org · repo https://github.com/OpenDengue/master-repo · VERIFIED (2026-11-08, listed repo contents)
- File: `https://raw.githubusercontent.com/OpenDengue/master-repo/main/data/releases/V1.3.1/Temporal_extract_V1_3_1.zip` (zip 55 MB, csv ~504 MB) · VERIFIED (2026-11-08, downloaded)
- License: CC BY 4.0 per OpenDengue site · UNVERIFIED (from web search; re-check on opendengue.org before poster)
- Citation: Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. (2024). A global dataset of publicly available dengue case count data. *Sci Data* 11(1):296.
- Columns: `adm_0_name, adm_1_name, adm_2_name, full_name, ISO_A0, FAO_GAUL_code, RNE_iso_code, IBGE_code, calendar_start_date, calendar_end_date, Year, dengue_total, case_definition_standardised, S_res, T_res, UUID` · VERIFIED (2026-11-08, read header)
- Thailand (`ISO_A0 == 'THA'`) total rows: 27,259 · VERIFIED (2026-11-08, pandas)
- Thailand, `S_res == 'Admin1'` and `T_res == 'Month'`: **27,024 rows, 78 distinct `adm_1_name`, 1993-01-01 to 2022-12-01** · VERIFIED (2026-11-08, pandas)
- Thailand national monthly (Admin0): 183 rows, 2010-01 to 2025-03; yearly Admin0: 52 rows, 1958–2009 · VERIFIED (2026-11-08)
- `dengue_total` over all Thai rows: median 18, max 174,285, min 0 · VERIFIED (2026-11-08)
- `adm_2_name` has mixed types (DtypeWarning) — read with `low_memory=False` or `dtype=str` · VERIFIED
- Why 78 names for 77 provinces: **UNVERIFIED** (resolved in T03)
- Weekly province-level data: **not available** in OpenDengue for Thailand · VERIFIED (2026-11-08)
- Data ends 2022-12; later years not available at province level · VERIFIED

### Weather — Open-Meteo Historical Weather API
- Docs: https://open-meteo.com/en/docs/historical-weather-api · UNVERIFIED (not yet called)
- License / terms: UNVERIFIED (believed CC BY 4.0; non-commercial free tier). Check before poster.
- Needs province centroid lat/lon table (built in T02, source to be recorded).

## 4. Glossary
- **Outbreak month:** label = 1 per §1.4.
- **Train / validation / test:** per §2, by calendar year.
- **Baseline:** simplest comparator listed in §2; any model must beat it on recall without collapsing precision.
- **Leakage:** any feature or threshold using information from after the prediction time or from validation/test years.

## 5. Changelog
- 2026-11-08 — v1 created by orchestrator from approved plan.
