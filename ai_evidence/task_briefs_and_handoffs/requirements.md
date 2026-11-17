# Course requirements (from "DS Capstone Project Requirements 1.pdf")
Source of truth for grading. The PDF is in the repo root.

## Overview
Course CPE312 (2569). Groups of 3–4 pick one SDG problem, use real open data, do the full data-science process. **Problem framing is graded most.** Output: A2 poster (gallery walk) + runnable Colab notebook. Worth 15% of course grade.

## 7 poster requirements (CRISP-DM)
| ID | Requirement | CRISP-DM | Poster must show |
|---|---|---|---|
| R1 | Sensible problem | Business Understanding | Users and decision, prediction time, measurable target, metric with reasoning |
| R2 | Verifiable data | Data Understanding / Preparation | Source and license, size, data problems found and how handled, train/test split method |
| R3 | EDA findings | Data Understanding | At least 1 key chart with conclusion |
| R4 | Model vs baseline | Modeling | Simple baseline vs group model using the R1 metric |
| R5 | Know where model fails | Evaluation | Failure examples/patterns with reasons |
| R6 | Practical recommendation | Deployment | What the user should do, cost, limits the data cannot prove |
| R7 | AI-use log | — | Questions asked, what AI gave, what the group changed and why (at least one rejection/correction) |

## R1: five framing questions (all must be answered)
1. Who uses the forecast and for what decision?
2. When is the prediction made, and does the input data exist at that time (no leakage)?
3. What does one row (attributes) represent?
4. Is the target measurable and clearly defined?
5. Which error is costlier? (Justifies the metric.)

## Data rules
- Open data, cite source, link, license (in R2). Do EDA and build a model.
- About 1,000+ rows (else explain the effect on reliability).
- Time-ordered data: split train/test **by time**, not randomly.
- Always include a simple baseline.
- Poster: header with group name, SDG, topic, members + roles; QR code to Colab notebook and data source. Charts for R3/R4 from the notebook; **every number on the poster must match the notebook**.

## Deadlines
- Fri Nov 6, 2026: register group + topic (Google Sheet) — already passed; tell instructor.
- Tue Nov 17, 2026, 13:00–16:00: gallery walk; Colab link submitted before start.

## Gallery walk and AI use
- Two rounds of ~25–30 min; one member stays at the poster, rotate. Every member must explain every requirement. Instructor asks random members about any requirement or any notebook cell. Dot stickers: best problem, best failure analysis, best recommendation.
- AI is an assistant, not the doer. R7 needs at least one case of rejecting/correcting AI output. Inability to explain own work loses Q&A points.

## Submission
Poster A2 (R1–R7 + header), Colab link (shared with instructor, runs start to end), data source + license links, individual peer evaluation form.

## Rubric (100%)
| Criterion | % | From |
|---|---|---|
| 1. Problem statement and goal alignment | 30 | R1 |
| 2. Data analysis and methods (2.1 prep + EDA 15, 2.2 analysis/ML 15) | 30 | R2, R3, R4, notebook |
| 3. Findings and insights (interpretation 10, recommendation 10) | 20 | R4, R5, R6 |
| 4. Presentation and visualization | 10 | whole poster, R3, R4 |
| 5. Teamwork | 5 | header roles + peer evaluation |
| 6. Q&A | 5 | gallery walk |
