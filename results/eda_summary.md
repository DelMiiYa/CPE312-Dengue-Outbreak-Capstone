# Exploratory Data Analysis (EDA) Summary: Thailand Dengue & Climate

**Generated for:** Poster Section R3 (and supporting evidence for R1, R2)  
**Data source:** `data/processed/panel.csv` (27,720 rows, 77 provinces, 1993–2022)  
**Configuration source:** `config/params.yaml`  
**Numerical source:** `results/eda_stats.json` (all statistics strictly verified from code)

---

## 1. Primary Key Chart Recommendation for Poster Box R3

**Recommended Primary Chart:** `results/figures/eda_seasonality.png`  
**Alternative / Complementary Chart for Box R2/R4:** `results/figures/eda_lag_correlation.png`

### Rationale
- **Immediate Visual Impact:** On an A2 poster, viewers and evaluators need to grasp the core epidemiological phenomenon in 5 seconds. `eda_seasonality.png` clearly reveals the 12-month transmission cycle across Thailand, illustrating how the summer temperature peak in April (28.60°C) and the monsoon rainfall onset in May (189.84 mm) precede the epidemic dengue surge in July (114.31 cases/province).
- **Direct Link to Decision R1:** Demonstrates why provincial public health offices (สสจ.) must make interventions (larval-source removal) 1 month ahead in May/June before the July epidemic explosion.
- **Support from Lag Correlations:** `eda_lag_correlation.png` serves as the empirical justification for Section R4 (Feature Engineering), proving that temperature leads transmission by 2–3 months ($r \approx 0.39$ to $0.42$) and rainfall leads by 0–1 month ($r \approx 0.29$).

---

## 2. Quantitative Findings by Figure

### Figure 1: Monthly Seasonal Profile (`results/figures/eda_seasonality.png`)
*Computed strictly on train years 1993–2015 (23 years, 20,556 reported province-months).*

1. **Epidemic Peak in July:**
   - Dengue cases reach their nationwide peak in **Month 7 (July)** with a provincial mean of **114.31 cases/province/month** (median: **51.00**, total cases: **197,531**).
   - Transmission remains elevated in August (mean: **100.65**) and June (mean: **101.55**).
2. **Transmission Trough in February:**
   - The lowest transmission occurs in **Month 2 (February)** with a provincial mean of **17.88 cases/province/month** (median: **7.00**, total cases: **30,891**), closely followed by January (mean: **19.30**).
   - Peak-to-trough ratio across the seasonal cycle is **6.39x** ($114.31 / 17.88$).
3. **Climate Precursor Dynamics:**
   - **Temperature Peak in April:** Mean temperature reaches its annual maximum in **Month 4 (April)** at **28.60°C** (trough in December at **23.86°C**).
   - **Monsoon Onset in May:** Mean precipitation doubles from **94.11 mm** in April to **189.84 mm** in May, peaking in September at **267.58 mm**.
   - **Biological Interpretation:** Elevated April temperatures accelerate viral replication (shortening the extrinsic incubation period in *Aedes aegypti*), while May monsoon rains create extensive breeding habitats, driving the July outbreak peak.

---

### Figure 2: Weather Lag Correlations (`results/figures/eda_lag_correlation.png`)
*Computed strictly on train years 1993–2015. Lags 0 to 4 months computed within each province (`groupby('province_en').shift(k)`) to prevent cross-province boundary leakage.*

1. **Temperature Leads Cases by 2–3 Months:**
   - **Median within-province Pearson $r$:** Lag 0 = **0.1345**, Lag 1 = **0.2686**, **Lag 2 = 0.3909** (IQR: [0.2912, 0.4549]), **Lag 3 = 0.3940** (IQR: [0.3057, 0.4684]), Lag 4 = **0.2833**.
   - **Pooled $\log(1 + \text{cases})$ Pearson $r$:** Lag 0 = **0.2685**, Lag 1 = **0.3689**, **Lag 2 = 0.4219**, **Lag 3 = 0.3904**, Lag 4 = **0.2718**.
   - **Significance:** Temperature is the strongest leading weather indicator, peaking 2 to 3 months prior to dengue transmission.
2. **Rainfall and Humidity Lead Cases by 0–1 Month:**
   - **Precipitation:**
     - Median within-province $r$: **Lag 0 = 0.2853** (IQR: [0.1665, 0.3505]), **Lag 1 = 0.2290** (IQR: [0.1629, 0.2735]), Lag 2 = **0.0759**, Lag 3 = **-0.1054**, Lag 4 = **-0.2469**.
     - Pooled $\log(1 + \text{cases})$ $r$: **Lag 0 = 0.2895**, **Lag 1 = 0.2256**, Lag 2 = **0.0677**, Lag 3 = **-0.1339**, Lag 4 = **-0.3031**.
   - **Relative Humidity:**
     - Median within-province $r$: **Lag 0 = 0.2857**, **Lag 1 = 0.1818**, Lag 2 = **-0.0002**, Lag 3 = **-0.1981**, Lag 4 = **-0.3371**.
     - Pooled $\log(1 + \text{cases})$ $r$: **Lag 0 = 0.3046**, **Lag 1 = 0.1973**, Lag 2 = **0.0041**, Lag 3 = **-0.1959**, Lag 4 = **-0.3384**.
3. **Feature Selection Validation:**
   - At prediction time $t$ for target month $t+1$, weather observed at month $t$ corresponds to transmission lag 1, and weather at $t-1$ corresponds to transmission lag 2.
   - The empirical peaks for temperature (lags 2–3) and rainfall (lags 0–1) are therefore fully observable at prediction time $t$, directly validating the parameter configuration `weather_lags: [0, 1, 2, 3]` in `config/params.yaml`.

---

### Figure 3: Province Heterogeneity & Outbreak Threshold Justification (`results/figures/eda_province_heterogeneity.png`)
*Computed strictly on train years 1993–2015.*

1. **Extreme Baseline Disparity (49.78x):**
   - **National Baseline (Train):** Mean = **53.72 cases/month**, Standard Deviation = **126.37 cases/month**. Single national threshold ($\text{Mean} + 1\cdot\text{SD}$) = **180.09 cases**.
   - **Highest Province:** **Bangkok** — Mean = **354.45 cases/month**, SD = **463.80**, Median = **187.50**, Max = **4,273.00**, Local Threshold = **818.26**.
     - Bangkok's monthly average is **6.60x** higher than the national average.
     - Top 5 provinces by mean cases: Bangkok (**354.45**), Nakhon Ratchasima (**152.45**), Nakhon Si Thammarat (**145.31**), Chiang Mai (**133.16**), Surin (**112.67**).
   - **Lowest Province:** **Nong Bua Lamphu** — Mean = **7.12 cases/month**, SD = **13.04**, Median = **3.00**, Max = **97.00**, Local Threshold = **20.17**.
     - Bottom 5 provinces by mean cases: Nong Bua Lamphu (**7.12**), Sing Buri (**8.12**), Satun (**12.59**), Ranong (**12.83**), Samut Songkhram (**13.75**).
   - **Ratio of Highest to Lowest Province:** **49.78x** ($354.45 / 7.12$).
2. **Definitive Justification for Per-Province Threshold ($\text{mean}_p + 1\cdot\text{SD}_p$):**
   - **The 11 Masked Provinces:** Exactly **11 provinces** (Amnat Charoen, Ang Thong, Bueng Kan, Mukdahan, Nakhon Nayok, Nong Bua Lamphu, Ranong, Samut Songkhram, Satun, Sing Buri, Trat) have a historical maximum case count in the train period that is strictly lower than the national threshold of **180.09 cases**.
   - Under a single national cutoff, **14.3% of Thailand's provinces would NEVER trigger an outbreak alert**, leaving their local health offices with zero warnings even during record local epidemics.
   - Conversely, Bangkok's median monthly cases (**187.50**) already exceeds the national threshold (**180.09**), triggering constant false alarms in over 50% of months.
   - This empirically confirms the decision in SSOT §1.4 to calculate local thresholds per province on train years only.

---

### Figure 4: Annual Trends & The COVID-19 Anomaly (`results/figures/eda_annual_trend_covid.png`)
*Computed across the full panel 1993–2022 (30 years).*

1. **Historical Epidemic Cycles:**
   - Top 5 epidemic years: **1998** (**124,557 cases**), **2001** (**104,671 cases**), **1997** (**99,153 cases**), **2019** (**87,866 cases**), and **2013** (**87,502 cases**).
   - Multi-year periodicity indicates cyclic vector and serotype transmission patterns occurring roughly every 2 to 5 years.
2. **The 2021 COVID-19 Collapse (11.30x Drop):**
   - Annual dengue cases dropped from **87,866 cases** in 2019 to **50,911** in 2020, collapsing to an all-time 30-year low of **7,778 cases** in **2021** before recovering to **34,605** in 2022.
   - Ratio between pre-pandemic 2019 and pandemic 2021 is **11.30x** ($87,866 / 7,778$).
   - Concurrently, the share of province-months with zero reported cases surged from **1.19%** in 2019 and a baseline of ~3–5% to **24.13%** in 2021 and **12.77%** in 2022.
   - **Epidemiological Drivers:** Nationwide school closures, restricted domestic mobility, lockdown curfews, and public hospital avoidance during peak COVID-19 waves severely curtailed both transmission opportunity and case reporting.
3. **Period Breakdown Supporting Split Design:**
   - **Train Period (1993–2015, 23 years):** **1,104,249 cases** total.
   - **Validation Period (2016–2017, 2 years):** **70,309 cases** total (2016: **38,466**, 2017: **31,843**).
   - **Test Period (2018–2022, 5 years):** **236,236 cases** total.
     - **Normal Test Subperiod (2018–2019):** **142,942 cases** (2018: **55,076**, 2019: **87,866**).
     - **COVID-Affected Test Subperiod (2020–2022):** **93,294 cases** (2020: **50,911**, 2021: **7,778**, 2022: **34,605**).
   - Directly justifies the SSOT §2 requirement to evaluate model performance both across the full test set and separately within normal (2018–2019) vs COVID-affected (2020–2022) subperiods.

---

## 3. Summary of Files Generated

| File | Purpose | Resolution / Format |
|---|---|---|
| `src/eda/run_eda.py` | Complete reproducible pipeline script | Python 3.13 |
| `results/figures/eda_seasonality.png` | Monthly dengue cases alongside rainfall and temperature | 300 DPI PNG (566 KB) |
| `results/figures/eda_lag_correlation.png` | Within-province and pooled lag correlations (lags 0–4) | 300 DPI PNG (566 KB) |
| `results/figures/eda_province_heterogeneity.png` | Case distribution disparity & threshold justification | 300 DPI PNG (494 KB) |
| `results/figures/eda_annual_trend_covid.png` | 30-year epidemic timeline, splits, and COVID drop | 300 DPI PNG (514 KB) |
| `results/eda_stats.json` | Single verifiable source for all cited statistics | JSON |
| `tests/test_eda.py` | Unit tests for artifact existence and anti-leakage compliance | pytest (5 passed) |
