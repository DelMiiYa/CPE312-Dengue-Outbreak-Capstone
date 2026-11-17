# เดือนหน้าไข้เลือดออกระบาดไหม? (Will Dengue Break Out Next Month?)
### Province-Level 1-Month-Ahead Dengue Outbreak Early Warning System in Thailand (1993–2022)

**CPE312 Data Science Capstone Project (Academic Year 2569)** · **SDG 3: Good Health and Well-being (Target 3.3)**

---

## 🔗 Key Project Links

- **Runnable Standalone Google Colab Notebook:** [`capstone_dengue.ipynb` on Google Colab](https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS)
- **Google Drive Deliverables Folder (Poster, Guides, Data Bundle):** [`CPE312_DS_Capstone_Dengue_Deliverables`](https://drive.google.com/drive/folders/1xd2lGvq065ZsCDYC8Xd-Dh3sx2ooZgxe)
- **Evidence of Conversations with AI (R7 Governance & Prompts):** [`ai_evidence/`](ai_evidence/) · [`AI_Conversation_Evidence_CPE312.md`](ai_evidence/AI_Conversation_Evidence_CPE312.md) · [`AI_Conversation_Evidence_CPE312.pdf`](ai_evidence/AI_Conversation_Evidence_CPE312.pdf)
- **Thai A2 Poster Content & QR Codes:** [`poster/poster_R1_to_R7_th.md`](poster/poster_R1_to_R7_th.md)
- **Gallery Walk Guides:** [English (`results/gallery_walk_guide.md`)](results/gallery_walk_guide.md) · [Thai (`results/gallery_walk_guide_th.md`)](results/gallery_walk_guide_th.md)

---

## 📋 CRISP-DM Summary (R1–R7)

| Req | CRISP-DM Stage | Key Details & Verified Results |
|---|---|---|
| **R1** | **Business Understanding** | **User:** Provincial Public Health Offices (สสจ.) in all 77 Thai provinces deciding 1 month ahead on vector control, VHV (อสม.) mobilization, and hospital surge readiness.<br>**Prediction clock:** End of month *t* for month *t+1* (zero future weather or look-ahead leakage).<br>**Target:** `outbreak(p, t+1) = 1` if `cases(p, t+1) > μ_p + 1.0 × SD_p` (per-province threshold fit strictly on 1993–2015 train years).<br>**Primary Metric:** **Recall on outbreak months** (False Negatives carry high clinical and human cost). |
| **R2** | **Data Understanding & Prep** | **Sources (CC BY 4.0):** OpenDengue V1.3.1 (`27,024` Admin1 monthly rows) + Open-Meteo ERA5 (`27,720` province-month rows, `0` weather NaNs).<br>**Data Fixes:** Merged duplicate Prachin Buri spelling (`PRACHIN BURI` 1993–2002 + `PHACHINBURI` 2003–2022) to restore canonical 77 provinces; preserved `696` pre-establishment NAs for 5 newer provinces in `panel.csv` and excluded them from `modeling_table.csv` (`26,100` rows, `0` NaNs).<br>**Chronological Split:** Train `1994–2015` (`19,632` rows), Val `2016–2017` (`1,848` rows), Test `2018–2022` (`4,620` rows; Normal `2018–2019` vs. COVID `2020–2022`). |
| **R3** | **EDA Findings** | **Climate Leads:** April temperature peak (`28.60°C`) leads July dengue peak (`114.31` cases/province) by 2–3 months (lag-3 `r = 0.3940`); May monsoon onset (`189.84 mm`) leads by 0–1 month (`r = 0.2853`).<br>**Spatial Disparity (`49.78×`):** Bangkok (`354.45` cases/mo) vs. Nong Bua Lamphu (`7.12` cases/mo); a single national cutoff (`180.09`) would leave **11 provinces** with zero alerts over 30 years.<br>**COVID-19 Structural Break:** Cases dropped `11.30×` from `87,866` (2019) to `7,778` (2021). |
| **R4** | **Model vs. Baseline** | **Test Set (2018–2022, 392 outbreaks):**<br>- Majority Class: `0.00%` Recall<br>- Seasonal (`t-12`): `28.32%` Recall, `0.1453` PR-AUC<br>- Persistence (`t-1`): `62.24%` Recall, `0.4255` PR-AUC (`148` FN)<br>- Logistic Regression (`thr=0.54`): `85.97%` Recall, `0.7702` PR-AUC<br>- Random Forest (`thr=0.45`): `82.91%` Recall, `0.7698` PR-AUC<br>- **HistGradientBoosting (`thr=0.49` from Val `F2`):** **`88.27%` Recall (`346/392`)**, `53.98%` Precision, `0.7657` PR-AUC (`+26.02 pp` over Persistence, `-68.9%` FN reduction; `89.22%` Recall normal vs. `86.18%` COVID). |
| **R5** | **Error Analysis** | **Onset vs. Ongoing:** Across `148` sudden outbreak onsets, Persistence gets **`0.0%` Recall (`0/148`)** while HistGradientBoosting catches **`73.0%` (`108/148`)** (and `97.5%` on ongoing outbreaks). `87.0%` of HGB's `46` FNs are abrupt `3.35×` spikes.<br>**False Positive Anatomy (`295` FPs):** **`93.6%`** are actionable (41.0% near-misses, 36.9% epidemic cool-down tails, 15.6% 2-month early warnings); only `6.4%` are pure false alarms. |
| **R6** | **Policy & Cost Dominance** | **Two-Tier Protocol:** Green (`< 0.35`, `83.8%` months, `0.90%` risk) → Yellow Watch (`0.35–0.65`, `17.12%` risk, VHV larval removal) → Red High Alert (`≥ 0.65`, `60.53%` risk, ULV fogging & hospital surge).<br>**Combined Capture:** **`91.07%` (`357/392` outbreaks)**, reducing total cost by **`65.9%–69.7%`** vs. a 6-month blanket rainy-season campaign for all cost penalty ratios `R ≥ 3`. |
| **R7** | **AI Oversight & Evidence** | Full human-in-the-loop governance documented in [`ai_evidence/`](ai_evidence/), including 7 verified cases where AI outputs were rejected or corrected (random splits, national cutoffs, Accuracy bias, hallucinated `shapely` centroids, `HistGradientBoosting.feature_importances_` crash, plot overlaps, and extra dependencies). |

---

## 📁 Repository Structure

```text
DS_capstone/
├── ai_evidence/                      # Evidence of AI conversations, selected prompts, R7 log, & PDF
│   ├── AI_Conversation_Evidence_CPE312.md
│   ├── AI_Conversation_Evidence_CPE312.pdf
│   └── task_briefs_and_handoffs/     # Tracked copies of AGENTS.md, SSOT.md, WORKLOG.md, T01–T12 briefs/handoffs
├── config/
│   └── params.yaml                   # Single configuration file for seeds, splits, lags, and paths
├── data/
│   ├── raw/                          # Filtered THA OpenDengue CSV, monthly Open-Meteo CSV, & SOURCE_*.md
│   └── processed/                    # panel.csv, modeling_table.csv, province_thresholds.csv, predictions
├── notebooks/
│   └── capstone_dengue.ipynb         # Executed standalone Colab/Jupyter notebook (20 cells, 7 inline PNGs)
├── poster/
│   ├── poster_R1_to_R7_th.md         # Complete Thai A2 poster content (R1–R7)
│   └── qr_*.png                      # Scannable QR codes (Colab, OpenDengue, Open-Meteo)
├── results/
│   ├── figures/                      # 300-DPI publication figures (EDA, R4, R5, R6)
│   ├── *.json                        # Machine-generated metrics, EDA, error, feature, & policy artifacts
│   ├── *_report.md / recommendations.md / gallery_walk_guide*.md / .pdf
├── src/
│   ├── data/                         # fetch_opendengue.py, fetch_weather.py, build_panel.py
│   ├── eda/                          # run_eda.py
│   ├── features/                     # build_features.py
│   ├── models/                       # baselines.py, train_models.py, error_analysis.py, recommend_policy.py
│   ├── notebook/                     # build_notebook.py
│   └── poster/                       # build_poster_content.py, build_qa_and_r7.py, qrcode_gen.py
└── tests/                            # 82 automated pytest verification & anti-leakage tests
```

---

## 🧪 Verification & Reproduction

Run the full automated test suite (verifying data integrity, zero temporal leakage, model metrics, scannable QR codes, and 100% concordance across notebook, JSON artifacts, poster, and reports):

```bash
pytest -v
```

Expected output: **`82 passed`**.

To rebuild the pipeline from the processed/raw datasets in the repository:

```bash
python src/features/build_features.py
python src/models/baselines.py
python src/models/train_models.py
python src/models/error_analysis.py
python src/models/recommend_policy.py
python src/notebook/build_notebook.py
python src/poster/build_poster_content.py
python src/poster/build_qa_and_r7.py
```

---

## 📜 Data Licenses & Citations

- **Dengue Surveillance Data:** [OpenDengue V1.3.1](https://opendengue.org) (`CC BY 4.0`). Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. (2024). *A global dataset of publicly available dengue case count data.* *Sci Data* 11(1):296.
- **Historical Climate Data:** [Open-Meteo Historical Weather API (ERA5 Reanalysis)](https://open-meteo.com/en/docs/historical-weather-api) (`CC BY 4.0`, non-commercial).
