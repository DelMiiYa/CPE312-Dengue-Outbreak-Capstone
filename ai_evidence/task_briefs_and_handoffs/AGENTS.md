# AGENTS.md — read this first (every agent, every session)

Project: CPE312 DS Capstone, SDG 3. "Will dengue break out next month?" Province × month classification, Thailand.
Repo root: `E:\Antigravity-Projects\DS_capstone`. This `_agent/` folder is git-ignored coordination space.

## Reading order
1. This file
2. `_agent/docs/SSOT.md` — facts, definitions, locked decisions. **Authoritative.**
3. Your task brief: `_agent/tasks/<TASK-ID>/brief.md`
4. `config/params.yaml` — every number the code uses.

If any of these disagree, the SSOT wins. If the brief conflicts with the SSOT, stop and say so in the handoff.

## Rules
1. Stay inside the brief's scope. Do not start other tasks.
2. **Never invent** data facts, column names, file paths, package APIs or metric values. If unsure, verify by running code (`df.columns`, `df.shape`, `help(...)`) or mark the item `UNVERIFIED` in the handoff and ask.
3. **Numbers come from code.** Parameters live in `config/params.yaml`; results go to `results/metrics.json`. Never type a result number by hand into text.
4. Do **not** edit `_agent/docs/SSOT.md`. Put proposals under "SSOT change requests" in your handoff.
5. No new dependencies without asking. Available: Python 3.13, pandas 3.0, scikit-learn 1.9, matplotlib. Not installed: lightgbm, pyarrow (use CSV).
6. Time-series rule: split by time, never random. Any threshold, scaler, or encoder is fit on **train years only**.
7. Run the acceptance commands in the brief and paste the **real output** into the handoff. Do not claim success without running them.
8. Before stopping: write `handoff.md` in your task folder (use `_agent/templates/handoff.md`) and append one line to `_agent/logs/WORKLOG.md`.
9. Code and docs in English. Keep code simple and readable; each group member must be able to explain every line.
10. Small, testable modules in `src/`; tests in `tests/`; large data in `data/` (git-ignored, rebuilt by scripts).

## Handoff flow
Orchestrator writes `brief.md` → you implement → you write `handoff.md` + WORKLOG entry → reviewer writes `review.md` (PASS / FIX) → next task unlocks (see `_agent/tasks/INDEX.md`).

## WORKLOG line format
`YYYY-MM-DD HH:MM | agent-name | TASK-ID | action | result | next`
Also log every time an AI suggestion was **rejected or corrected**, and why (feeds poster section R7).
