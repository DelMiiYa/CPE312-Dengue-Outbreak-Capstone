# Handoff — T01 Fetch OpenDengue, filter Thailand Admin1 monthly
Worker: worker · Date: 2026-11-08 16:10

## What was done
1. Implemented idempotent data fetcher in `src/data/fetch_opendengue.py` using `requests` and `pandas`.
2. Downloaded OpenDengue V1.3.1 archive (`Temporal_extract_V1_3_1.zip`) from official repository to `data/raw/`.
3. Computed SHA-256 checksum and extracted `Temporal_extract_V1_3_1.csv`.
4. Filtered dataset for Thailand Admin1 monthly records (`ISO_A0 == 'THA' & S_res == 'Admin1' & T_res == 'Month'`) using memory-safe chunking and `dtype={'adm_2_name': str}`.
5. Saved filtered dataset to `data/raw/opendengue_tha_admin1_month.csv` maintaining all 16 original columns.
6. Verified license text directly from `https://opendengue.org` (confirmed CC BY 4.0) and documented provenance, checksum, statistics, license, and citations in `data/raw/SOURCE_opendengue.md`.
7. Tested idempotency (skips download and unzipping if archive already present) and confirmed exact match with SSOT expectations.

## Files created / changed
- `src/__init__.py`
- `src/data/__init__.py`
- `src/data/fetch_opendengue.py`
- `data/raw/Temporal_extract_V1_3_1.zip` (git-ignored)
- `data/raw/Temporal_extract_V1_3_1.csv` (git-ignored)
- `data/raw/opendengue_tha_admin1_month.csv` (git-ignored)
- `data/raw/SOURCE_opendengue.md` (git-ignored by `data/`)
- `_agent/tasks/T01-fetch-opendengue/handoff.md`
- `_agent/logs/WORKLOG.md`

## Commands run and real output

### 1. Initial run of fetch_opendengue.py
Command: `python src/data/fetch_opendengue.py`
Output:
```
Downloading from https://raw.githubusercontent.com/OpenDengue/master-repo/main/data/releases/V1.3.1/Temporal_extract_V1_3_1.zip to data\raw\Temporal_extract_V1_3_1.zip...
Progress: 52.6 MB / 52.6 MB (100.0%)
Download complete.
Computing SHA-256 checksum of zip archive...
SHA-256: 6bb4dbec3d891e444047354619d7bc7003e29e2f9f9cfcec29130fe605c126a2
Extracting Temporal_extract_V1_3_1.zip...
Extracted: data\raw\Temporal_extract_V1_3_1.csv
Filtering Temporal_extract_V1_3_1.csv for Thailand Admin1 monthly records...
Filtered CSV saved to data\raw\opendengue_tha_admin1_month.csv
Source metadata saved to data\raw\SOURCE_opendengue.md

--- Verification Summary ---
Shape: (27024, 16)
Unique adm_1_name: 78
Date range: 1993-01-01 to 2022-12-01

SUCCESS: All acceptance criteria match SSOT exactly!
```

### 2. Brief acceptance criterion 2 verification
Command: `python -c "import pandas as pd; d=pd.read_csv('data/raw/opendengue_tha_admin1_month.csv'); print(d.shape, d.adm_1_name.nunique(), d.calendar_start_date.min(), d.calendar_start_date.max())"`
Output:
```
(27024, 16) 78 1993-01-01 2022-12-01
```

### 3. Idempotency test (second run)
Command: `python src/data/fetch_opendengue.py`
Output:
```
Zip archive already exists at data\raw\Temporal_extract_V1_3_1.zip, skipping download.
Computing SHA-256 checksum of zip archive...
SHA-256: 6bb4dbec3d891e444047354619d7bc7003e29e2f9f9cfcec29130fe605c126a2
Extracting Temporal_extract_V1_3_1.zip...
CSV already extracted: data\raw\Temporal_extract_V1_3_1.csv
Filtering Temporal_extract_V1_3_1.csv for Thailand Admin1 monthly records...
Filtered CSV saved to data\raw\opendengue_tha_admin1_month.csv
Source metadata saved to data\raw\SOURCE_opendengue.md

--- Verification Summary ---
Shape: (27024, 16)
Unique adm_1_name: 78
Date range: 1993-01-01 to 2022-12-01

SUCCESS: All acceptance criteria match SSOT exactly!
```

## Results
- Extracted shape: `(27024, 16)`
- Unique provinces (`adm_1_name`): `78`
- Date range: `1993-01-01` to `2022-12-01`
- Raw dataset row count: `2,834,996`
- Raw Thailand total rows: `27,259`
- Filtered Thailand Admin1 monthly rows: `27,024`
- SHA-256 of `Temporal_extract_V1_3_1.zip`: `6bb4dbec3d891e444047354619d7bc7003e29e2f9f9cfcec29130fe605c126a2`

## Acceptance criteria status
| # | Criterion | Result (PASS / FAIL) | Evidence |
|---|---|---|---|
| 1 | `python src/data/fetch_opendengue.py` runs to completion | PASS | Completed with exit code 0 |
| 2 | Shape `(27024, 16)`, 78 provinces, 1993-01-01 to 2022-12-01 | PASS | Output: `(27024, 16) 78 1993-01-01 2022-12-01` |
| 3 | Re-running script a second time does not re-download | PASS | Script reported `Zip archive already exists ... skipping download` |
| 4 | `SOURCE_opendengue.md` contains URL, date, sha256, row count, license, citation | PASS | Verified all fields in `data/raw/SOURCE_opendengue.md` |

## Deviations from the brief
None.

## UNVERIFIED items
None.

## SSOT change requests
- In SSOT §3 "Dengue cases — OpenDengue V1.3.1", update:
  - `License: CC BY 4.0 per OpenDengue site · UNVERIFIED (from web search; re-check on opendengue.org before poster)`
  → to:
  - `License: CC BY 4.0 per OpenDengue site · VERIFIED (2026-11-08, checked https://opendengue.org footer notice)`

## Suggested next steps
- Reviewer checks T01 handoff and sets status to PASS in `_agent/tasks/INDEX.md`.
- Proceed with T02 (Fetch Open-Meteo monthly weather + centroid table).
