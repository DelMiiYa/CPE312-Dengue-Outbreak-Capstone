# Evidence of Conversations with AI During the Capstone Project (CPE312)

**Project Title:** **เดือนหน้าไข้เลือดออกระบาดไหม?** — *Will Dengue Break Out Next Month? Province-Level 1-Month-Ahead Dengue Outbreak Prediction in Thailand (1993–2022)*  
**SDG Alignment:** SDG 3 — Good Health and Well-being (Target 3.3: Combat communicable/tropical diseases)  
**GitHub Repository:** `https://github.com/DelMiiYa/CPE312-Dengue-Outbreak-Capstone`  
**Standalone Google Colab Notebook:** `https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS`  
**Google Drive Deliverables Folder:** `https://drive.google.com/drive/folders/1xd2lGvq065ZsCDYC8Xd-Dh3sx2ooZgxe`  

---

## 1. In What Parts of the Project Do Students Use AI?
*(คำตอบข้อ 4: นิสิตใช้ AI ในส่วนใดของโครงงานบ้าง)*

### English Summary
We used AI strictly as a **Human-in-the-Loop pair programmer and research assistant** (never as an autonomous replacement) across six structured stages of our CRISP-DM workflow:

1. **Problem Scoping & Data Source Verification (R1–R2):** Checking dataset availability, temporal/spatial granularity (`Admin1` × `Month`), and `CC BY 4.0` licensing for **OpenDengue V1.3.1** and **Open-Meteo Historical Weather (ERA5)**, and structuring our Single Source of Truth (`SSOT.md`) and five R1 framing answers.
2. **Data Ingestion & Quality Auditing Scripts (R2):** Drafting modular Python pipelines (`fetch_opendengue.py`, `fetch_weather.py`, `build_panel.py`) to download and aggregate 30 years of daily weather for 77 Thai provinces, reconcile the 78th raw province name (`PRACHIN BURI` 1993–2002 + `PHACHINBURI` 2003–2022), and audit the 696 pre-establishment missing months across 5 newer provinces.
3. **EDA & Publication Chart Prototyping (R3):** Writing Matplotlib plotting code for our 300-DPI figures (seasonality peaks, lag cross-correlations, `49.78×` provincial heterogeneity, and the `11.30×` COVID-19 disruption), which we inspected visually and corrected for overlapping text and legend placement.
4. **Causal Feature Engineering & Automated Leakage Testing (R2 / R4):** Implementing grouped time-lag features (`build_features.py`) and writing automated `pytest` verification suites (`test_features_and_leakage.py`) enforcing zero look-ahead bias and strict train-only threshold calibration (`1993–2015`).
5. **Model Training, Error Decomposition & Policy Simulation (R4–R6):** Generating scikit-learn pipelines (`LogisticRegression`, `RandomForestClassifier`, `HistGradientBoostingClassifier` tuned via Validation `F2`-score), decomposing test errors into Onset vs. Ongoing outbreaks and actionable False Positives (`93.6%`), and simulating the Two-Tier (Green/Yellow/Red) parametric cost model (`R ≥ 3`).
6. **Reproducible Packaging, Poster Automation & Q&A Prep (R7):** Packaging a self-contained Google Colab notebook with Drive bundle bootstrapping, implementing a zero-dependency QR code generator, synchronizing poster figures dynamically from `results/*.json`, and organizing bilingual Q&A rehearsal materials.

### สรุปภาษาไทย (Thai Version)
กลุ่มของเราใช้ AI ในฐานะ **"ผู้ช่วยร่วมคิดและผู้ช่วยเขียนโค้ดภายใต้การกำกับของมนุษย์" (Human-in-the-Loop Assistant)** ใน 6 ส่วนหลักของกระบวนการ CRISP-DM ได้แก่:

1. **การสำรวจแหล่งข้อมูลและวางกรอบปัญหา (R1–R2):** ใช้ช่วยค้นหาและตรวจสอบความพร้อมของฐานข้อมูลเปิด (OpenDengue V1.3.1 และ Open-Meteo ERA5 ภายใต้ CC BY 4.0) รวมถึงการวางโครงสร้างเอกสารควบคุมความถูกต้อง (`SSOT.md`) และคำตอบเกณฑ์ตั้งโจทย์ 5 ข้อ
2. **การเขียนสคริปต์ดึงข้อมูลและตรวจสอบคุณภาพข้อมูล (Data Preparation):** ใช้ช่วยร่างโค้ด Python ดึงข้อมูลสภาพอากาศรายวัน 30 ปี ของ 77 จังหวัดมารวมเป็นรายเดือน และตรวจสอบความผิดปกติ เช่น การพบชื่อจังหวัดปราจีนบุรีซ้ำ 2 รูปแบบ และ 696 เดือนที่ว่างของ 5 จังหวัดตั้งใหม่
3. **การสร้างกราฟสำรวจข้อมูลเบื้องต้น (EDA & Visualization — R3):** ใช้ช่วยร่างโค้ด Matplotlib สำหรับพล็อตกราฟฤดูกาล, Lag Correlation และความเหลื่อมล้ำระหว่างจังหวัด 49.78 เท่า ซึ่งสมาชิกนำมาตรวจทานและปรับแก้ตำแหน่งป้ายข้อความด้วยตนเอง
4. **วิศวกรรมฟีเจอร์และชุดทดสอบป้องกันข้อมูลรั่วไหล (Feature Engineering & Unit Testing):** ใช้ช่วยเขียนโค้ดสร้างตัวแปรย้อนหลัง (Lag/Rolling Features) และเขียนชุดทดสอบอัตโนมัติ (`pytest` รวม 82 ข้อ) เพื่อยืนยันว่าไม่มีการรั่วไหลของข้อมูลอนาคต (Zero Data Leakage)
5. **การรันโมเดลเปรียบเทียบและจำลองนโยบายความคุ้มค่า (Modeling, Error Analysis & Policy — R4–R6):** ใช้ช่วยเขียนโค้ดฝึกสอนโมเดล (`LogisticRegression`, `RandomForest`, `HistGradientBoosting` จูนเกณฑ์ตัดสินบน Validation ด้วย `F2`-Score), แยกประเภทความผิดพลาด Onset vs. Ongoing, และจำลองความคุ้มค่าของระบบเตือนภัย Two-Tier (เขียว/เหลือง/แดง)
6. **การจัดทำโค้ดพร้อมส่งมอบและเอกสารเตรียมนำเสนอ (Documentation & Reproducibility):** ใช้ช่วยประกอบ Google Colab Notebook ที่รันได้แบบ Standalone, สร้าง QR Code โดยไม่พึ่งไลบรารีภายนอก, และจัดทำคู่มือซ้อมตอบคำถามสำหรับ Gallery Walk

---

## 2. Selected Prompts Demonstrating Clear Problem Understanding & Accurate Communication
*(คำตอบข้อ 3: ตัวอย่าง Prompt ที่แสดงถึงความเข้าใจปัญหาและความสามารถในการสื่อสารงานอย่างแม่นยำ)*

Instead of issuing vague one-line commands like *"build a dengue prediction model for me"*, we authored structured engineering specifications grounded in epidemiology, temporal causality, and verifiable acceptance tests. Below are three verified prompts from our project workflow (`T05`, `T07`, and `T08`/`T09`).

### Prompt A (Primary Recommendation — Feature Engineering, Target Definition & Anti-Leakage Verification in `T05`)

> **Prompt Given to AI (from `_agent/tasks/T05-features-labels/brief.md`):**  
> "Read `_agent/AGENTS.md` and `_agent/docs/SSOT.md`, then implement `src/features/build_features.py` and `tests/test_features_and_leakage.py` to build the leak-free supervised modeling table (`data/processed/modeling_table.csv`) from `data/processed/panel.csv` and `config/params.yaml`.
>
> **Problem & Domain Constraints:**  
> 1. **Decision & Prediction Horizon:** Provincial Public Health Offices (สสจ.) in 77 Thai provinces make resource allocation decisions at the end of month t for month t+1. Every predictor at row (p, t) must use data strictly from month ≤ t (no future weather or look-ahead leakage).  
> 2. **Province-Specific Outbreak Target (Train-Only Fitting):** Because dengue burden varies by ~50x across provinces (e.g., Bangkok vs. Nong Bua Lamphu), do not use a single national threshold. For each province p, filter strictly to training years (`1993 <= year <= 2015`) and compute `mean_p = cases.mean()`, `sd_p = cases.std(ddof=1)`, and `threshold_p = mean_p + 1.0 * sd_p`. Define target `outbreak_t1 = 1` if `cases(p, t+1) > threshold_p` else `0`.  
> 3. **Causal Lag Features:** Sort strictly by `['province_en', 'year', 'month']` and group by `province_en` before shifting. Compute `cases_lag_0..3`, 3-month rolling mean `cases_roll_mean_3` (months t, t-1, t-2), train-standardized `cases_zscore_lag_0 = (cases_lag_0 - mean_p) / sd_p`, weather lags `0..3` for temperature, precipitation, and humidity, cyclical month encodings (`sin_target_month`, `cos_target_month`), and baseline flags (`outbreak_lag_0`, `outbreak_same_month_last_year` at t-11).  
> 4. **Missing Data & Chronological Split:** Do not impute fake case counts for the 696 pre-establishment months of the 5 newly created provinces (e.g., Bueng Kan before 2011); drop pre-establishment and initial lag warmup rows and log the exact row accounting in `results/feature_summary.json`. Split strictly by `target_year`: Train `1994–2015`, Validation `2016–2017` (1,848 rows), and Test `2018–2022` (4,620 rows, subdivided into Normal `2018–2019` and COVID-19 `2020–2022`).  
> 5. **Verification Criteria:** Write `pytest` unit tests proving that (a) mutating case counts in years ≥ 2016 does not change `province_thresholds.csv`, and (b) mutating cases or weather at month t+1 does not change any feature column at month t."

#### Why This Prompt Demonstrates Problem Understanding (เหตุผลที่ Prompt นี้แสดงความเข้าใจโจทย์):
- **Domain Alignment:** Explicitly connects feature boundaries to the real public-health decision clock (end of month *t* for *t+1*) and vector/administrative realities (50x spatial disparity across provinces and non-existent historical data before Bueng Kan split from Nong Khai in 2011).
- **Zero-Leakage Specification:** Translates abstract "avoid data leakage" advice into concrete engineering invariants (`groupby('province_en')` before `.shift()`, train-only `mean_p` and `sd_p`, and `target_year`-based chronological splitting).
- **Test-Driven Accountability:** Defines falsifiable `pytest` mutation assertions so the AI's output can be mechanically proven leak-free.

---

### Prompt B (Model Training, Asymmetric Error Cost & Validation-Only Tuning in `T07`)

> **Prompt Given to AI (from `_agent/tasks/T07-models/brief.md`):**  
> "Train and evaluate `LogisticRegression`, `RandomForestClassifier`, and `HistGradientBoostingClassifier` on `data/processed/modeling_table.csv` against three locked baselines (Majority Class, Persistence t-1, and Seasonal t-12) following these strict rules:  
> 1. **Zero Test Leakage:** Fit scalers and models strictly on `split == 'train'` (19,632 rows, 1994–2015). Tune hyperparameters and the probability operating threshold strictly on `split == 'val'` (1,848 rows, 2016–2017) by maximizing the F2-score (weighting Recall 2x higher than Precision, because missed outbreaks [False Negatives] leave hospitals unprepared and cost far more than false alarms).  
> 2. **Frozen Evaluation Across Regimes:** Lock the validation-selected model and operating threshold before evaluating once on `split == 'test'` (2018–2022 overall, plus `2018–2019` Normal vs. `2020–2022` COVID-19 structural-break subperiods).  
> 3. **Verification:** Save all metrics to `results/metrics.json`, export row-level predictions (`val_predictions.csv`, `test_predictions.csv`), and verify with `pytest` unit tests that no target or future columns enter feature matrix `X`."

---

### Prompt C (Error Decomposition & Parametric Policy Trade-off Analysis in `T08`/`T09`)

> **Prompt Given to AI (from `_agent/tasks/T08-error-analysis/brief.md` & `T09-recommendations/brief.md`):**  
> "Partition the 392 test outbreak months into Onset months (`outbreak_lag_0 == 0` and `outbreak_t1 == 1`, where Persistence mathematically gets 0% recall) vs. Ongoing months (`outbreak_lag_0 == 1` and `outbreak_t1 == 1`), decompose the 295 False Positives into post-outbreak cool-down tails, near-misses above `mean_p`, and 2-month early warnings (`outbreak_t2 == 1`), and design a Two-Tier Alert Protocol (Green `< 0.35`, Yellow Watch `0.35–0.65` at 0.3 cost units, Red Alert `≥ 0.65` at 1.0 cost unit). Never invent a single baht cost; instead evaluate parametric total cost `Alerts + R × Missed` across sensitivity ratios `R ∈ {3, 5, 10, 15}` against no-alert, blanket rainy-season (May–Oct), and reactive persistence policies."

---

## 3. Reasoning Behind Interpreting & Applying AI Suggestions: Revising the Overall Pipeline Concept
*(คำตอบข้อ 5: เหตุผลเบื้องหลังการตีความคำแนะนำของ AI และการประยุกต์ใช้เพื่อปรับปรุงแนวคิดไปป์ไลน์ทั้งระบบ)*

### English — Short Version
Early in the project, we observed that standard single-chat AI prompting suffers from three critical risks in data science: (1) **context drift and numerical inconsistency** between code outputs and written reports, (2) **library/API hallucinations** (e.g., calling non-existent attributes or unnecessary geospatial packages), and (3) **defaulting to naive ML boilerplate** that violates epidemiological and time-series constraints (such as random `train_test_split` look-ahead leakage or a uniform national outbreak cutoff).

Rather than patching errors ad hoc, we **revised our entire engineering pipeline concept** into a deterministic, human-governed **Orchestrator → Single Source of Truth (`SSOT.md`) → Scoped Task Handoff (`T01`–`T12`) → Automated `pytest` Verification** architecture:
1. **Single Source of Truth & Code-Driven Numbers:** We locked all problem definitions, chronological split boundaries (Train 1994–2015, Val 2016–2017, Test 2018–2022), and lag parameters in `SSOT.md` and `config/params.yaml`. Every script exports structured metrics to `results/*.json`, and downstream reports/posters dynamically read from those JSON files so AI never types a metric by hand.
2. **Preprocessing & Model Refinements Enforced by Pipeline:** Through scoped task briefs, we rejected random splitting and uniform national thresholds (which would leave 11 low-population provinces with zero alerts over 30 years due to a 49.78× burden gap), enforcing train-only per-province thresholds (`μ_p + 1.0 × SD_p`) and dropping 696 pre-establishment months across 5 newly created provinces instead of fabricating imputed values. For modeling, we replaced naive Accuracy/0.50 cutoffs with Validation `F2`-score threshold tuning (`0.49` on `HistGradientBoosting`, achieving **88.27% Test Recall** and **73.0% Onset Recall** vs. **0.0%** for Persistence) and designed a **Two-Tier (Yellow 0.35 / Red 0.65)** alert protocol (**91.07% combined recall**).
3. **Code Modifications & 82 Automated Unit Tests:** When AI hallucinated `shapely`/`pyproj` LAEA centroid projections or called `.feature_importances_` on scikit-learn's `HistGradientBoostingClassifier`, our review gate caught the errors immediately; we replaced them with direct GeoJSON coordinate parsing and Validation `permutation_importance`, and locked in an **82-test `pytest` suite** auditing zero data leakage and 100% cross-deliverable numerical consistency.

### English — Detailed Version
1. **How We Interpreted AI's Suggestions (Our Critical Reasoning):**  
   We treated the AI as a fast pair-programmer for boilerplate code, API syntax, and documentation drafting, but **never as an authoritative decision-maker**. Our core reasoning was that LLMs optimize for plausible-looking standard templates (such as random cross-validation, uniform global thresholds, or accuracy optimization) that silently fail in real-world epidemiological time-series forecasting. Therefore, every AI recommendation had to pass three human filters: **(a) Epidemiological & Operational Validity** (does this help a Provincial Public Health Office [สสจ.] act 1 month ahead?), **(b) Strict Temporal Causality** (does any future information leak into month *t*?), and **(c) Empirical Execution** (does the code run cleanly without extra dependencies and pass unit tests?).
2. **How We Applied & Revised Recommendations Across the Project:**
   - **Revising the Overall Pipeline Concept:** To eliminate hallucinated numbers and context loss across tasks, we redesigned the workflow around a central `_agent/docs/SSOT.md` and `config/params.yaml`, breaking the CRISP-DM lifecycle into 12 gated tasks (`T01`–`T12`). Each task required a strict specification (`brief.md`), pasted terminal verification outputs (`handoff.md`), and a quality audit (`review.md`), while logging every rejected AI suggestion in `WORKLOG.md`.
   - **Refining Preprocessing Steps:** When AI suggested standard random splitting and a single national outbreak cutoff (180.09 cases/month), our EDA revealed a **49.78× burden ratio** between Bangkok (354.45 cases/month) and Nong Bua Lamphu (7.12 cases/month), which would permanently silence 11 small provinces. We modified the preprocessing pipeline (`build_features.py`) to compute province-specific thresholds (`μ_p + 1.0 × SD_p`) strictly on 1993–2015 training years, merged duplicate historical spellings (`PRACHIN BURI` / `PHACHINBURI` into 77 canonical provinces), and dropped 696 pre-establishment months for 5 newer provinces rather than imputing synthetic surveillance counts.
   - **Adjusting the Model & Decision Policy:** Because outbreak months represent only 8.48% of the test set and missed outbreaks (False Negatives) carry severe human cost, we rejected standard 0.50 probability cutoffs and tuned our models on the 2016–2017 Validation split by maximizing the **F2-score** (yielding threshold `0.49` for `HistGradientBoosting`, achieving **88.27% Test Recall**). After error analysis showed that 86.96% (87.0%) of False Negatives were sudden monsoon onsets and 93.56% (93.6%) of False Positives were clinically useful near-misses, epidemic tails, or 2-month early warnings, we refined the deployment concept into a **Two-Tier Decision Protocol** (Green `< 0.35`, Yellow Watch `0.35–0.65` for low-cost volunteer larval removal, Red Alert `≥ 0.65` for EOC & fogging), capturing **91.07% of outbreaks** and reducing total cost by **65.9%–69.7%** vs. blanket rainy-season campaigns for all penalty ratios `R ≥ 3`.
   - **Modifying Code & Enforcing 82 Automated Tests:** We stripped out hallucinated external dependencies (`shapely`/`pyproj` in `fetch_weather.py`, `tabulate` in `build_notebook.py`, and third-party `qrcode` in `qrcode_gen.py`), replaced the broken `hgb.feature_importances_` call with Validation `permutation_importance` in `train_models.py`, fixed Matplotlib annotation overlaps across 6 publication figures, and wrote 82 `pytest` tests verifying zero data leakage and 100% numerical concordance across all project deliverables.

### ภาษาไทย — ฉบับสรุปและฉบับละเอียด (Thai Short & Detailed Versions)
- **แนวคิดหลักในการตีความและปรับไปป์ไลน์ (Short TH):**  
  ในช่วงเริ่มต้น เราพบว่าการใช้ AI ในแชทเดียวแบบทั่วไปมีความเสี่ยง 3 ด้าน คือ (1) **Context Drift** ทำให้ตัวเลขในโค้ดกับรายงานไม่ตรงกัน, (2) **API/Dependency Hallucination** เช่น การเรียกใช้ไลบรารีที่ไม่มีในเครื่อง หรือ `.feature_importances_` ที่ใช้กับ `HistGradientBoostingClassifier` ไม่ได้, และ (3) **การใช้ค่าเริ่มต้นแบบ Naive ML** ที่ละเมิดกฎอนุกรมเวลา (เช่น สุ่ม `train_test_split` ทำให้เกิด Data Leakage หรือใช้เกณฑ์ระบาดค่าเดียวทั่วประเทศจน 11 จังหวัดเล็กไม่เคยได้รับการเตือนภัยเลย)  
  เราจึง **ปรับแนวคิดไปป์ไลน์ทั้งระบบ (Pipeline Concept Revision)** จากการถามตอบทีละครั้ง มาเป็นสถาปัตยกรรม **Orchestrator → `SSOT.md` & `config/params.yaml` → Scoped Task Briefs (`T01`–`T12`) → Handoff & Reviewer Gate → ชุดทดสอบ `pytest` 82 ข้อ** โดยบังคับให้ตัวเลขทุกตัวต้องคำนวณจากโค้ดและบันทึกลง `results/*.json`, ใช้เกณฑ์ระบาดจำเพาะรายจังหวัด (`μ_p + 1.0 × SD_p`) จากปี Train เท่านั้น, จูนเกณฑ์ตัดสินโมเดลบน Validation ด้วย `F2`-Score (`0.49` ทำ Test Recall **88.27%** และจับ Onset **73.0%** เทียบ Persistence **0.0%**), และต่อยอดเป็นนโยบาย Two-Tier ที่จับการระบาดได้ **91.07%** พร้อมลดต้นทุนลง 65.9%–69.7% เมื่อเทียบกับการรณรงค์ปูพรมหน้าฝน

---

## 4. Complete R7 AI Oversight & Correction Log (All 7 Verified Cases)

Every case below is logged in `ai_evidence/task_briefs_and_handoffs/WORKLOG.md` and audited by `tests/test_deliverables_ready.py`:

| Case | Task(s) | Prompt / Context Given to AI | What AI Suggested / Generated | Defect Caught by Human Verification | Human Correction & Pipeline Impact |
|:---:|:---:|---|---|---|---|
| **Case 1** | **T05 / T07** *(Data Splitting)* | Asked for train/test splitting code on the province × month dengue panel. | Proposed random `train_test_split(X, y, test_size=0.2, shuffle=True, random_state=42)` or K-Fold CV. | **Temporal Data Leakage:** Shuffling leaks future months into training data, violating causality and inflating metrics unrealistically. | **Rejected AI code; locked chronological split in `SSOT.md`:** Train `1994–2015`, Val `2016–2017`, Test `2018–2022` (Normal `2018–2019` vs. COVID `2020–2022`), enforced by `test_features_and_leakage.py`. |
| **Case 2** | **T04 / T05** *(Target Threshold)* | Asked for a Thailand dengue outbreak threshold formula across 77 provinces. | Proposed a single national cutoff `μ_national + 1.0 × σ_national = 180.09 cases/month`. | **Extreme Spatial Blindspot (49.78× spread):** Bangkok averages `354.45` cases/month vs. Nong Bua Lamphu `7.12`. A single cutoff leaves **11 provinces** with zero alerts over 30 years. | **Rejected national threshold; enforced train-only per-province cutoffs (`μ_p + 1.0 × σ_p`)** fit strictly on `1993–2015` in `province_thresholds.csv`. |
| **Case 3** | **T06 / T07** *(Metric & Threshold Tuning)* | Asked which evaluation metric and decision cutoff to optimize for dengue outbreak alerts. | Recommended Accuracy / ROC-AUC and default `0.50` classification threshold. | **Class Imbalance Trap:** Outbreaks are only `8.48%` of test rows; predicting all zeros gets `91.52%` Accuracy with `0.0%` Recall. | **Rejected Accuracy; standardized on Recall + PR-AUC + Validation `F2`-Score maximization** (yielding `0.49` cutoff for `HistGradientBoosting`, `88.27%` Recall). |
| **Case 4** | **T02** *(Geospatial Centroids)* | Asked for centroid extraction code for 77 Thai provinces for Open-Meteo ERA5 API calls. | Generated complex Lambert Azimuthal Equal Area (LAEA) projection code requiring `shapely` and `pyproj` (and referenced it in docs). | **Hallucination & Dependency Bloat:** Neither `shapely` nor `pyproj` was installed (violating `AGENTS.md` Rule 5), and `provinces.geojson` already contained precomputed `properties.lat` and `properties.lon`. | **Stripped hallucinated LAEA code & updated `SOURCE_weather.md`** to read `properties.lat/lon` directly with Python stdlib + pandas (`0` NaNs across `27,720` rows). |
| **Case 5** | **T07** *(Feature Importance)* | Asked to extract feature importances from `HistGradientBoostingClassifier`. | Generated `hgb.feature_importances_`. | **API Incompatibility (`AttributeError`):** scikit-learn's `HistGradientBoostingClassifier` does not expose `.feature_importances_`. | **Replaced with Validation `permutation_importance` (`scoring="average_precision"`, `n_repeats=5`)**, preventing train overfitting and ranking `cases_zscore_lag_0` (`0.6367`) and `precip_lag_3` (`0.0464`). |
| **Case 6** | **T04 / T07 / T08 / T09** *(Visualization Layout)* | Generated Matplotlib scripts for EDA lag correlation, R4 model comparison, R5 error anatomy, and R6 Two-Tier policy figures. | Placed data labels, callout boxes, and legends directly over bars and plotted lines. | **Visual Overlap Defects:** Numerical labels collided with bars/boxes on `eda_lag_correlation.png`, `r4_model_vs_baseline.png`, `r5_error_analysis.png` (Panels A & D), and `r6_threshold_policy.png` (Panel B). | **Manually adjusted `ylim` padding, 2-column legends, callout coordinates, and white `bbox` backgrounds** across all 300-DPI figures. |
| **Case 7** | **T09 / T10 / T11 / T12** *(Mathtext, Zero-Dependency & Hardcoded Numbers)* | Generated Matplotlib headers, table formatters, QR code utilities, and poster builders. | Used `\ge` in Matplotlib mathtext (crash), proposed external packages (`tabulate`, `qrcode`), and left hardcoded `0.31`/`0.46` LR/RF thresholds in `build_poster_content.py`. | **Runtime Crashes, Rule 5 Violations & Stale Numbers:** Matplotlib rejected `\ge`; extra packages violated Rule 5; hardcoded thresholds disagreed with `results/metrics.json` (`0.54` / `0.45`). | **Fixed `\geq`, replaced `tabulate`/`qrcode` with native pandas `.to_string()` + standalone `GF(256)` Reed-Solomon QR encoder (verified via `cv2.QRCodeDetector`), and pulled all numbers dynamically from `results/*.json`.** |

---

## 5. Chronological Transcript Log of AI Sessions (Nov 8–17, 2026)

Below is the authentic chronological record extracted from our Antigravity conversation transcripts and `_agent/logs/WORKLOG.md`, documenting how human prompts guided AI through every project phase:

### Phase 1: Project Ideation, R1 Framing & Multi-Agent Architecture (`Conv 1e73cef2`, Nov 8, 2026)
- **`2026-11-08 14:53` — User Prompt:** *"read the pdf and give me summary"*  
  - **AI Action:** Extracted and summarized `DS Capstone Project Requirements 1.pdf` (6 pages, R1–R7 rubric, 5 framing criteria, time-split rule, and R7 AI-rejection requirement).
- **`2026-11-08 15:10` — User Prompt:** *"im thinking sdg3 good health, help me think of a project"* → followed by **`15:12`:** *"3 people, thai data, 1 week if possible also anwer in english from now on, plan only for now"* → **`15:16`:** *"classification and check the data availibity, SDGs ที่เลือก / ชื่อหัวข้อโปรเจ็ค / โจทย์คือ / แหล่งข้อมูล (แนบลิ้งค์) fill out theses for me"*  
  - **AI Action:** Researched OpenDengue & DDC surveillance availability, verified CC BY 4.0 licensing, and formulated the R1 problem statement for Thai Provincial Public Health Offices (สสจ.).
- **`2026-11-08 15:23` — User Prompt:** Provided the course topic registration table row (`พยากรณ์เดือนที่เกิดการระบาดของโรคไข้เลือดออกรายจังหวัดในประเทศไทยล่วงหน้า 1 เดือน`) and asked AI to name the project consistently with the class format → yielded **"เดือนหน้าไข้เลือดออกระบาดไหม?"**
- **`2026-11-08 15:30` — User Prompt:** *"/plan let's start planning the project, we will use another smaller ai agent to write code and review if needed, handing it off using a task folder with handoff for each task and create an ssot for all other ai agent and log work so there is less hallucination"*  
  - **User Plan Approval (`15:38`):** Selected manual task handoff across project chats, approved building a verified 77-province centroid table for weather, initialized git with `_agent/` ignored, and locked English for code/docs and Thai for poster + summary.
  - **Outcome (`T00`):** Orchestrator scaffolded `_agent/AGENTS.md`, `_agent/docs/SSOT.md`, `config/params.yaml`, `_agent/logs/WORKLOG.md`, templates, and briefs `T01`–`T03`.

### Phase 2: Data Acquisition & Panel Cleaning (`T01`–`T03`, Nov 8–9, 2026)
- **`2026-11-08 16:06` (`Conv cacdc904`, `T01` Worker):** *"Read _agent/AGENTS.md, then _agent/docs/SSOT.md, then do the task in _agent/tasks/T01-fetch-opendengue/brief.md"*  
  - **Outcome:** Built `src/data/fetch_opendengue.py`; extracted `27,024` Thailand Admin1 monthly rows (`78` distinct `adm_1_name`, `1993-01` to `2022-12`) and verified `CC BY 4.0` license. Reviewed & passed `16:15`.
- **`2026-11-09 13:18` (Orchestrator Check):** User asked *"i have questions about the result of this project plan, the R1-7 are the results mentioned in the project requirement pdf, is it included in the project plan"* → Orchestrator mapped R1–R7 explicitly to `T01`–`T12`.
- **`2026-11-09 13:21` (`Conv 5527f13a`, `T02` Worker):** *"Read _agent/AGENTS.md, then _agent/docs/SSOT.md, then complete the task in _agent/tasks/T02-fetch-weather/brief.md"*  
  - **Outcome & R7 Correction (`14:55`):** Worker fetched `27,720` province-month rows (`77` provinces, `0` NaNs) from Open-Meteo ERA5; reviewer caught and fixed hallucinated LAEA/`shapely` centroid documentation in `fetch_weather.py` and `SOURCE_weather.md` (**R7 Case 4**).
- **`2026-11-09 15:00` (`Conv 94e9a24e`, `T03` Worker):** *"Read _agent/AGENTS.md, then _agent/docs/SSOT.md, then complete the task in _agent/tasks/T03-clean-merge/brief.md"*  
  - **Outcome:** Proved the 78th name (`PRACHIN BURI` 1993–2002 + `PHACHINBURI` 2003–2022) represented non-overlapping halves of Prachin Buri; built `panel.csv` (`27,720` rows, `77` provinces) and documented the `696` pre-establishment missing months (`10/10` tests passing).

### Phase 3: EDA, Leak-Free Features & Modeling (`T04`–`T07`, Nov 9, 2026)
- **`2026-11-09 15:23` (`Conv c3bc682e`, `T04` EDA Worker & `Conv 837ffaee`, `T05` Features Worker):** Parallel execution via scoped briefs.
  - **Outcome (`T04`):** Quantified April temperature lead (`28.60°C`, lag-3 `r = 0.3940`), July case peak (`114.31`), `49.78×` Bangkok-vs-Nong Bua Lamphu disparity (`11` provinces silenced under a national threshold), and `11.30×` COVID-19 drop (`87,866` in 2019 → `7,778` in 2021). Reviewer fixed overlapping bar labels in `eda_lag_correlation.png` (**R7 Case 6**).
  - **Outcome (`T05`):** Computed train-only `province_thresholds.csv`, created `modeling_table.csv` (`26,100` rows, `0` NaNs), and passed strict leakage mutation tests (`20/20` tests passing; **R7 Cases 1 & 2**).
- **`2026-11-09 15:39` (`Conv 36f897d0`, `T06` Baselines Worker) & `15:47` (`Conv c79b6dc3`, `T07` Models Worker):**  
  - **Outcome:** Evaluated 3 baselines vs. Logistic Regression (`85.97%` Recall), Random Forest (`82.91%` Recall), and HistGradientBoosting (`88.27%` Test Recall, `+26.02 pp` over Persistence `62.24%`, `-68.9%` FN reduction). Caught missing `.feature_importances_` on HGB (**R7 Case 5**) and fixed legend overlap on `r4_model_vs_baseline.png` (**R7 Case 6**; `35/35` tests passing).

### Phase 4: Error Analysis, Policy Design & Final Deliverables (`T08`–`T12`, Nov 9–10, 2026)
- **`2026-11-09 16:13` (`Conv 45e234cc`, `T08` Error Analysis Worker):** Quantified Onset (`73.0%` HGB vs. `0.0%` Persistence across `148` onsets) vs. Ongoing (`97.5%`), `87.0%` onset share of `46` FNs (`3.35×` jump), and `93.6%` clinical usefulness across `295` FPs (`43/43` tests passing).
- **`2026-11-09 16:36` (`Conv bb034a0b`, `T09` Policy Worker):** Designed the Two-Tier (Green `< 0.35`, Yellow `0.35–0.65`, Red `≥ 0.65`) operational protocol (`91.07%` recall) and proved ML cost dominance across all `R ≥ 3` (`65.9%–69.7%` cost savings vs. blanket rainy-season campaigns). Fixed Matplotlib `\ge` mathtext crash (**R7 Case 7**) and panel overlaps (**R7 Case 6**; `58/58` tests passing).
- **`2026-11-09 16:58` (`Conv ad877f05`, `T10` Notebook Worker):** Generated executed `notebooks/capstone_dengue.ipynb` (`20` cells, `7` inline PNGs, `0` errors); rejected `tabulate` dependency (**R7 Case 7**; `65/65` tests passing).
- **`2026-11-10 13:16` (`Conv b5e866b5`, `T11` Poster Worker):** Built Thai A2 poster content and standalone `GF(256)` QR code PNGs (rejecting external `qrcode` package; `74/74` tests passing).
- **`2026-11-10 13:33` (`Conv 94a16818`, `T12` Q&A/R7 Worker) & `13:50` (Reviewer):** Built `r7_ai_log_and_qa_prep.md` (7 cases, 20 flashcards, 3-min Thai pitch); reviewer caught and replaced hardcoded LR/RF thresholds (`0.31`/`0.46` → dynamic `0.54`/`0.45`) and fixed Flashcard 13 keys (`81/81` tests passing).

### Phase 5: Cloud Packaging, Gallery Walk Preparation & Submission (`Conv dc3a938e` & Current Session, Nov 11–17, 2026)
- **`2026-11-11 12:10` (`Conv 1e73cef2`):** Uploaded initial deliverables to Google Drive (`CPE312_DS_Capstone_Dengue_Deliverables`).
- **`2026-11-17 01:09 – 02:07` (`Conv dc3a938e`):**
  - User requested bilingual English & Thai Gallery Walk preparation guides converted to PDF via `mdtopdf`, plus a fully standalone Colab bootstrapping solution: *"/gdrive /plan create a fully standalone notebook in colab with downloading from gdrive"*.
  - AI built `capstone_colab_bundle.zip` (`1,407,003` bytes), updated Cell 1 of `capstone_dengue.ipynb` to auto-download from Drive (`1SLcdp1ovK76mL28IG_RNG6TaGjrfGLKx`), updated `qr_colab.png` and Drive deliverables in-place, and verified clean-directory execution (`82/82` tests passing).
- **`2026-11-17 15:24 – 15:42` (`Conv dc3a938e` & `Conv 4dd3672f`):** User requested concise submission-form answers, creation of this `ai_evidence/` documentation folder + PDF, and pushing the complete codebase to public GitHub repository `DelMiiYa/CPE312-Dengue-Outbreak-Capstone`.
