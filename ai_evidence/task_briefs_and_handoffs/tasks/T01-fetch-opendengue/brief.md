# Brief — T01 Fetch OpenDengue, filter Thailand Admin1 monthly
Status: TODO · Written by: orchestrator · Date: 2026-11-08

## Goal
Download OpenDengue V1.3.1, keep only Thailand province-level monthly rows, save as a small CSV, and record source/license/checksum.

## Why
Serves R2 (verifiable data). Depends on: T00.

## Inputs
- URL: `https://raw.githubusercontent.com/OpenDengue/master-repo/main/data/releases/V1.3.1/Temporal_extract_V1_3_1.zip` (zip ~55 MB, CSV inside ~504 MB)
- Do **not** reuse any file from outside this repo. Download it yourself.

## Outputs
- `src/data/fetch_opendengue.py` — idempotent script (skips download if zip already present)
- `data/raw/opendengue_tha_admin1_month.csv` — filtered rows, original column names kept
- `data/raw/SOURCE_opendengue.md` — URL, download date, sha256 of the zip, row counts, license text copied from opendengue.org (record the exact URL where you read it), citation

## Constraints
- Filter: `ISO_A0 == 'THA'` and `S_res == 'Admin1'` and `T_res == 'Month'`.
- Read the CSV with `low_memory=False` (column `adm_2_name` has mixed types). Use `usecols` and chunking if memory is tight.
- Zip and big CSV go in `data/raw/` (git-ignored). Do not commit data.
- Dependencies: standard library + pandas + `urllib`/`requests` only if already installed.

## Out of scope
Cleaning, name fixes, merging with weather (T03).

## Acceptance criteria (paste real output in handoff)
1. `python src/data/fetch_opendengue.py` runs to completion.
2. `python -c "import pandas as pd; d=pd.read_csv('data/raw/opendengue_tha_admin1_month.csv'); print(d.shape, d.adm_1_name.nunique(), d.calendar_start_date.min(), d.calendar_start_date.max())"` → expected per SSOT: `(27024, 16) 78 1993-01-01 2022-12-01`. Any mismatch must be reported, not hidden.
3. Re-running the script a second time does not re-download.
4. `SOURCE_opendengue.md` contains: URL, date, sha256, row count, license, citation.

## Known pitfalls
- The license in SSOT is UNVERIFIED. Read it on opendengue.org and quote it; report if it differs from CC BY 4.0.
- Do not print the full CSV; print shape and head only.
