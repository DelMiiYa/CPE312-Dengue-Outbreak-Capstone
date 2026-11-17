# Evidence of Conversations with AI — CPE312 Data Science Capstone (SDG 3)

**Project:** **เดือนหน้าไข้เลือดออกระบาดไหม?** (*Will Dengue Break Out Next Month?*)  
**Topic:** Province-Level 1-Month-Ahead Dengue Outbreak Early Warning System in Thailand (1993–2022)  
**Course:** CPE312 Introduction to Data Science — Capstone Project (Academic Year 2569)  
**Deliverable Links:**
- **GitHub Repository:** `https://github.com/DelMiiYa/CPE312-Dengue-Outbreak-Capstone`
- **Standalone Google Colab Notebook:** `https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS`
- **Google Drive Deliverables Folder:** `https://drive.google.com/drive/folders/1xd2lGvq065ZsCDYC8Xd-Dh3sx2ooZgxe`

---

## 📁 Contents of This Folder

1. **[`AI_Conversation_Evidence_CPE312.md`](AI_Conversation_Evidence_CPE312.md)** (and compiled print-ready PDF: **[`AI_Conversation_Evidence_CPE312.pdf`](AI_Conversation_Evidence_CPE312.pdf)**)
   - **Section 1:** *Where Students Used AI in the Project* (Bilingual EN & TH breakdown across all 6 stages of CRISP-DM).
   - **Section 2:** *Selected High-Quality Prompts Demonstrating Problem Understanding* (Verbatim engineering/domain prompts from our sessions, with analysis of why they communicate constraints rigorously rather than issuing brief commands).
   - **Section 3:** *Reasoning & Pipeline Concept Revision* (How the team critically evaluated AI defaults, revised the entire collaboration architecture into an SSOT + Scoped Task Handoff + `pytest` pipeline, and modified preprocessing, modeling, and code).
   - **Section 4:** *Complete R7 AI Oversight & Correction Log* (All 7 verified cases where AI suggestions were rejected or corrected with empirical reasoning).
   - **Section 5:** *Chronological Transcript Log of AI Sessions (Nov 8–17, 2026)* (Timestamped user prompts, agent roles, task outcomes, and verification logs across 15 sessions).
2. **[`task_briefs_and_handoffs/`](task_briefs_and_handoffs/)**
   - [`AGENTS.md`](task_briefs_and_handoffs/AGENTS.md) — Core rules enforced on every AI session (e.g., *Never invent numbers; parameters live in `config/params.yaml`; results go to `results/metrics.json`; time-series splits strictly by time; log all rejected AI suggestions for R7*).
   - [`SSOT.md`](task_briefs_and_handoffs/SSOT.md) — Locked Single Source of Truth containing verified dataset facts, target definitions, and R1–R7 decisions.
   - [`WORKLOG.md`](task_briefs_and_handoffs/WORKLOG.md) — Append-only chronological execution & R7 correction log across `T00`–`T12`.
   - [`INDEX.md`](task_briefs_and_handoffs/INDEX.md) & [`requirements.md`](task_briefs_and_handoffs/requirements.md) — Task dependency graph and rubric mapping.
   - [`tasks/T01-*` through `T12-*`](task_briefs_and_handoffs/tasks/) — All 12 scoped task `brief.md` (prompts/specifications), `handoff.md` (AI outputs + real terminal outputs), and `review.md` (human/reviewer audit verdicts).

---

## 🔄 Human-in-the-Loop AI Governance Workflow

Rather than relying on an unverified single-chat AI prompt, our group enforced a gated **Orchestrator → Single Source of Truth → Scoped Task Brief (`T01`–`T12`) → Worker Handoff → Reviewer Audit → 82 `pytest` Checks** architecture:

| CRISP-DM Stage | Poster Req | Task ID | Evidence in `task_briefs_and_handoffs/tasks/` | Key AI Use & Human Verification |
|---|---|---|---|---|
| **Business Understanding** | **R1** | `T00` | `SSOT.md`, `requirements.md` | Brainstorming SDG 3 ideas; locking R1 5 framing questions, 1-month lead time, and Recall metric |
| **Data Understanding / Prep** | **R2** | `T01`, `T02`, `T03` | `T01-fetch-opendengue/`, `T02-fetch-weather/`, `T03-clean-merge/` | Downloading OpenDengue & Open-Meteo ERA5; fixing hallucinated `shapely`/LAEA centroid code (R7 Case 4); merging 78th province (`PRACHIN BURI`/`PHACHINBURI`) |
| **EDA & Visualization** | **R3** | `T04` | `T04-eda/` | Prototyping 4 figures; discovering `49.78×` provincial disparity & `11.30×` COVID drop; fixing Matplotlib text overlaps (R7 Case 6) |
| **Feature Engineering & Split** | **R2 / R4** | `T05` | `T05-features-labels/` | Rejecting AI random `train_test_split` (R7 Case 1) & uniform national cutoff (R7 Case 2); writing leakage unit tests |
| **Modeling & Baselines** | **R4** | `T06`, `T07` | `T06-baselines/`, `T07-models/` | Rejecting Accuracy (R7 Case 3); fixing broken `.feature_importances_` on `HistGradientBoostingClassifier` (R7 Case 5); Val `F2`-score threshold tuning (`0.49`) |
| **Evaluation & Error Analysis** | **R5** | `T08` | `T08-error-analysis/` | Decomposing Onset vs. Ongoing recall (`73.0%` vs. `0.0%` Persistence) & 295 FP clinical anatomy (`93.6%` actionable) |
| **Deployment & Policy** | **R6** | `T09` | `T09-recommendations/` | Designing Two-Tier (Green/Yellow/Red) alert system (`91.07%` recall) & parametric cost dominance (`R ≥ 3`); fixing `\ge` mathtext bug (R7 Case 7) |
| **Packaging, Poster & R7** | **R7 / Colab** | `T10`, `T11`, `T12` | `T10-notebook/`, `T11-poster/`, `T12-r7-qa-rehearsal/` | Standalone Google Colab bundle; zero-dependency QR generator; Thai poster & Q&A rehearsal; 82/82 `pytest` verification |
