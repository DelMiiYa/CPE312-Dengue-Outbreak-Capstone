# Review — T01 Fetch OpenDengue, filter Thailand Admin1 monthly
Reviewer: orchestrator/reviewer · Date: 2026-11-08

## Verdict
PASS

## Checks run
| Check | Result |
|---|---|
| `src/data/fetch_opendengue.py` code inspection (params.yaml usage, chunked read, `dtype={"adm_2_name": str}`, exact filter) | PASS |
| Acceptance check 2: `opendengue_tha_admin1_month.csv` shape, `adm_1_name.nunique()`, min/max `calendar_start_date` | PASS — `(27024, 16) 78 1993-01-01 2022-12-01` |
| Zip SHA-256 verification against `SOURCE_opendengue.md` and `handoff.md` | PASS — `6bb4dbec3d891e444047354619d7bc7003e29e2f9f9cfcec29130fe605c126a2` |
| Acceptance check 3: Re-ran `python src/data/fetch_opendengue.py` for idempotency | PASS — skipped download and unzip, exited 0 |
| Live check of `https://opendengue.org` footer against quoted license in `SOURCE_opendengue.md` | PASS — exact match (`CC BY 4.0`) |
| `git status --short` check (`data/` git-ignored) | PASS — no raw data tracked |

## Issues found
| # | File:line | Problem | Required fix |
|---|---|---|---|
| — | — | None | — |

## Hallucination check
- Every claimed file/column/number verified against real output? yes
- Anything in handoff contradicting SSOT? no

## Notes for orchestrator
- Pending SSOT update from T01 handoff: mark OpenDengue license (`CC BY 4.0`) as `VERIFIED (2026-11-08, checked https://opendengue.org footer)`.
- Note on the 78 distinct `adm_1_name` strings (for 77 Thai provinces): `PRACHIN BURI` (1993–2002, 120 rows) and `PHACHINBURI` (2003–2022, 240 rows) are a spelling split of the same province; T03 will formally map and report this alongside late-starting provinces (`AMNAT CHAROEN`, `MUKDAHAN`, `NONG BUA LAMPHU`, `SA KAEO` from 2003; `BUNGKAN` from 2011).
