# Brief — T03 Clean and merge into a complete province-month panel
Status: TODO · Written by: orchestrator · Date: 2026-11-08

## Goal
Merge dengue cases with weather into one clean panel of province × month, with every data issue documented.

## Why
Serves R2 (data problems found and how handled). Depends on: T01 and T02 both PASS.

## Inputs
- `data/raw/opendengue_tha_admin1_month.csv`
- `data/raw/weather_monthly.csv`
- `src/data/province_centroids.csv`

## Outputs
- `src/data/province_map.csv` — columns: `adm_1_name_opendengue, province_en`; every mapping justified in the handoff
- `src/data/build_panel.py`
- `data/processed/panel.csv` — columns: `province_en, year, month, cases, temp_mean_c, precip_sum_mm` (+ humidity if present)
- `data/processed/data_quality_report.md` — plain-language list of every issue found, count, and treatment (feeds poster R2)

## Constraints
- **Do not impute or drop cases silently.** Every missing month, duplicate, or odd value is counted and reported.
- Do not use any split years, thresholds, or labels here. No modeling logic in this task.
- Resolve why OpenDengue has **78** distinct `adm_1_name` for 77 provinces (spelling variants, duplicates, a non-province entity, or Bueng Kan split from Nong Khai in 2011?). Look at the data and report evidence (name, years present, row counts). Do not guess.

## Out of scope
Lags, labels, train/test split (T05), plots (T04).

## Acceptance criteria (paste real output)
1. `python src/data/build_panel.py` runs to completion.
2. Panel has one row per (province, year, month) with **no duplicates**: `python -c "import pandas as pd; p=pd.read_csv('data/processed/panel.csv'); print(p.shape, p.duplicated(['province_en','year','month']).sum(), p.isna().sum().to_dict())"`.
3. Report, with numbers: number of provinces, months per province (min/max), count of missing province-months in cases (before any handling), count of zeros, count of negative or non-integer case values.
4. `data_quality_report.md` lists the answer to the 78-vs-77 question with evidence.
5. Report which provinces have cases starting after 1993 (e.g. Bueng Kan) and how they are handled. Recommend a handling rule in the handoff; do not apply it silently.

## Known pitfalls
- Case counts may be reported in uneven ways in early years (1993–1995). Describe what you see (e.g. share of zeros per year) without drawing modeling conclusions.
- `calendar_start_date` is the month key; derive year/month from it, not from `Year` alone.
