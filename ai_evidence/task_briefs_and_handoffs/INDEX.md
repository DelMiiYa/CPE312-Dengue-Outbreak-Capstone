# Task index
Status values: TODO · IN-PROGRESS · HANDED-OFF (waiting review) · FIX · PASS
A task starts only when everything it depends on is PASS.

| ID | Task | Serves | Depends on | Owner | Status |
|---|---|---|---|---|---|
| T00 | Scaffold, SSOT, AGENTS, templates | all | — | orchestrator | PASS |
| T01 | Fetch OpenDengue, filter Thailand Admin1 monthly | R2 | T00 | worker | PASS |
| T02 | Fetch Open-Meteo monthly weather + centroid table | R2, R3 | T00 | worker | PASS |
| T03 | Clean and merge, resolve 78th name, complete panel | R2 | T01, T02 | worker | PASS |
| T04 | EDA figures | R3 | T03 | worker | PASS |
| T05 | Features, label, time split, leakage tests | R1, R2 | T03 | worker | PASS |
| T06 | Baselines | R4 | T05 | worker | PASS |
| T07 | Models, tuning on validation | R4 | T05, T06 | worker | PASS |
| T08 | Evaluation + error analysis | R5 | T07 | worker | PASS |
| T09 | Cost / threshold analysis + recommendations | R6 | T08 | worker | PASS |
| T10 | Assemble Colab notebook | notebook | T01–T09 | worker | PASS |
| T11 | Poster content (Thai) + QR | poster | T10 | worker | PASS |
| T12 | R7 AI log, peer eval, Q&A rehearsal | R7, Q&A | all | worker | PASS |

T01 and T02 can run in parallel (separate chats).
