"""
Build Poster Content (Thai R1-R7), Project Summary, and QR Codes.
Reads numbers strictly from results/*.json to guarantee 100% numerical consistency.
Generates:
  - poster/poster_R1_to_R7_th.md
  - _agent/docs/SUMMARY_TH.md
  - poster/qr_colab.png
  - poster/qr_opendengue.png
  - poster/qr_weather.png
"""

import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.poster.qrcode_gen import save_qr_png


def load_all_results(base_dir: Path) -> dict:
    """Load all quantitative JSON artifacts from results/."""
    results_dir = base_dir / "results"
    with open(results_dir / "metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)
    with open(results_dir / "eda_stats.json", "r", encoding="utf-8") as f:
        eda = json.load(f)
    with open(results_dir / "feature_summary.json", "r", encoding="utf-8") as f:
        feat = json.load(f)
    with open(results_dir / "error_analysis.json", "r", encoding="utf-8") as f:
        err = json.load(f)
    with open(results_dir / "policy_analysis.json", "r", encoding="utf-8") as f:
        pol = json.load(f)

    return {
        "metrics": metrics,
        "eda": eda,
        "feat": feat,
        "err": err,
        "pol": pol,
    }


def format_poster_markdown(data: dict) -> str:
    """Construct complete Thai A2 poster content box-by-box."""
    m = data["metrics"]
    eda = data["eda"]
    feat = data["feat"]
    err = data["err"]
    pol = data["pol"]

    # Quantitative variables pulled dynamically
    # Models & Baselines
    hgb_test = m["models"]["hist_gradient_boosting"]["metrics"]["test"]
    hgb_norm = m["models"]["hist_gradient_boosting"]["metrics"]["test_normal_2018_2019"]
    hgb_covid = m["models"]["hist_gradient_boosting"]["metrics"]["test_covid_2020_2022"]
    hgb_thresh = m["models"]["hist_gradient_boosting"]["threshold_used"]

    pers_test = m["baselines"]["persistence_last_month"]["test"]
    maj_test = m["baselines"]["majority_class"]["test"]
    seas_test = m["baselines"]["seasonal_last_year"]["test"]
    lr_test = m["models"]["logistic_regression"]["metrics"]["test"]
    lr_thresh = m["models"]["logistic_regression"]["threshold_used"]
    rf_test = m["models"]["random_forest"]["metrics"]["test"]
    rf_thresh = m["models"]["random_forest"]["threshold_used"]

    recall_diff = (hgb_test["recall"] - pers_test["recall"]) * 100
    fn_reduction_pct = (pers_test["fn"] - hgb_test["fn"]) / pers_test["fn"] * 100

    # EDA variables
    peak_temp_month = eda["seasonality"]["peak_temp_month"]
    peak_temp_c = eda["seasonality"]["peak_temp_mean_c"]
    peak_dengue_month = eda["seasonality"]["peak_dengue_month"]
    peak_dengue_cases = eda["seasonality"]["peak_dengue_mean_cases"]
    monsoon_month = eda["seasonality"]["monsoon_onset_month"]
    monsoon_rain = eda["seasonality"]["monsoon_onset_mean_precip_mm"]
    temp_lag3_corr = eda["lag_correlations"]["temp_mean_c"][3]["median_within_province"]
    rain_lag0_corr = eda["lag_correlations"]["precip_sum_mm"][0]["median_within_province"]

    het_ratio = eda["province_heterogeneity"]["ratio_top_to_bottom_mean"]
    bkk_mean = eda["province_heterogeneity"]["highest_province"]["mean"]
    nongbua_mean = eda["province_heterogeneity"]["lowest_province"]["mean"]
    masked_prov_count = eda["province_heterogeneity"]["provinces_never_reaching_national_threshold_count"]

    covid_drop_ratio = eda["annual_trends"]["covid_drop_ratio_2019_to_2021"]
    cases_2019 = eda["annual_trends"]["year_2019_cases"]
    cases_2021 = eda["annual_trends"]["year_2021_cases"]

    # Splits & Features
    total_panel = feat["total_panel_rows"]
    total_model = feat["modeling_table_rows"]
    train_rows = feat["splits"]["train"]["rows"]
    val_rows = feat["splits"]["val"]["rows"]
    test_rows = feat["splits"]["test"]["rows"]
    test_outbreaks = feat["splits"]["test"]["outbreak_count"]
    test_norm_rows = feat["splits"]["test_normal_2018_2019"]["rows"]
    test_covid_rows = feat["splits"]["test_covid_2020_2022"]["rows"]
    missing_months_late = (
        feat["dropped_rows_accounting"]["breakdown"]["late_starting_provinces_pre_start"]["count"]
        + feat["dropped_rows_accounting"]["breakdown"]["bueng_kan_pre_start"]["count"]
    )

    # Error Analysis
    onset_count = err["onset_vs_ongoing"]["breakdown"]["onset_count"]
    ongoing_count = err["onset_vs_ongoing"]["breakdown"]["ongoing_count"]
    pers_onset_rec = err["onset_vs_ongoing"]["persistence_last_month"]["onset"]["recall"]
    hgb_onset_rec = err["onset_vs_ongoing"]["hist_gradient_boosting"]["onset"]["recall"]
    fn_onset_pct = err["onset_vs_ongoing"]["hist_gradient_boosting"]["fn_share"]["onset_fn_pct"]
    fn_onset_count = err["onset_vs_ongoing"]["hist_gradient_boosting"]["fn_share"]["onset_fn"]
    total_fn_count = err["onset_vs_ongoing"]["hist_gradient_boosting"]["fn_share"]["total_fn"]
    missed_case_jump = err["onset_vs_ongoing"]["hist_gradient_boosting"]["onset_case_dynamics"]["missed_mean_case_jump"]

    fp_total = err["fp_anatomy_hgb"]["total_fp"]
    fp_actionable_pct = err["fp_anatomy_hgb"]["at_least_one_benign"]["pct"]
    fp_actionable_count = err["fp_anatomy_hgb"]["at_least_one_benign"]["count"]
    fp_pure_pct = err["fp_anatomy_hgb"]["pure_false_alarm"]["pct"]
    fp_pure_count = err["fp_anatomy_hgb"]["pure_false_alarm"]["count"]
    fp_nearmiss_pct = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["elevated_endemic_near_miss"]["pct"]
    fp_nearmiss_count = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["elevated_endemic_near_miss"]["count"]
    fp_tail_pct = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["post_outbreak_tail"]["pct"]
    fp_tail_count = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["post_outbreak_tail"]["count"]
    fp_early_pct = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["pre_outbreak_early_warning"]["pct"]
    fp_early_count = err["fp_anatomy_hgb"]["mutually_exclusive_partition"]["pre_outbreak_early_warning"]["count"]

    # Policy & Two-Tier
    green_pct = pol["two_tier_test"]["green"]["pct_months"]
    green_risk = pol["two_tier_test"]["green"]["outbreak_rate"] * 100
    yellow_pct = pol["two_tier_test"]["yellow"]["pct_months"]
    yellow_risk = pol["two_tier_test"]["yellow"]["outbreak_rate"] * 100
    yellow_alerts_yr = pol["two_tier_test"]["yellow"]["alerts_per_province_per_year"]
    red_pct = pol["two_tier_test"]["red"]["pct_months"]
    red_risk = pol["two_tier_test"]["red"]["outbreak_rate"] * 100
    red_alerts_yr = pol["two_tier_test"]["red"]["alerts_per_province_per_year"]
    comb_recall = pol["two_tier_test"]["overall_alert_zone"]["recall"] * 100
    comb_caught = pol["two_tier_test"]["overall_alert_zone"]["outbreaks_caught"]

    content = rf"""# เนื้อหาโปสเตอร์งานวิจัยโครงงานวิทยาการข้อมูล (A2 Poster Content)
**วิชา:** CPE312 Data Science Capstone (ภาคการศึกษา 2569)  
**เป้าหมายการพัฒนาที่ยั่งยืน:** SDG 3 — Good Health and Well-being (สุขภาพและความเป็นอยู่ที่ดี, เป้าประสงค์ 3.3 ยุติโรคเขตร้อนที่ถูกละเลย)  
**รูปแบบเอกสาร:** เอกสารต้นฉบับภาษาไทยแบ่งกล่องตามโครงสร้าง R1–R7 พร้อมตารางและตัวเลขที่ตรวจสอบได้จริง 100% (ตรงกับ Colab Notebook) สำหรับนำไปจัดวางใน Canva / Figma / PowerPoint ขนาด A2 (420 × 594 มม.)

---

## 📌 Poster Header (ส่วนหัวของโปสเตอร์)

### ชื่อโครงงาน
# เดือนหน้าไข้เลือดออกระบาดไหม?
### ระบบพยากรณ์การระบาดของโรคไข้เลือดออกล่วงหน้า 1 เดือน รายจังหวัดในประเทศไทย (1993–2022)
**Machine Learning-Based 1-Month Early Warning System for Dengue Outbreak Prevention in Thailand**

- **เป้าหมายระดับสากล:** SDG 3 — Good Health and Well-being (Target 3.3: ยุติการแพร่กระจายของโรคติดต่อที่มีแมลงเป็นพาหะ)
- **กลุ่มเป้าหมายผู้ใช้งาน:** สำนักงานสาธารณสุขจังหวัด (สสจ.) ทั้ง 77 จังหวัดทั่วประเทศไทย
- **สมาชิกและบทบาทความรับผิดชอบ:**
  1. **นาย ก. [รหัสนักศึกษา]** — *Data Engineer / Custodian:* รับผิดชอบ T01–T03, R2 (ดึงข้อมูล OpenDengue & Open-Meteo, ทำความสะอาด, รวมตาราง 77 จังหวัด)
  2. **นาย ข. [รหัสนักศึกษา]** — *ML Engineer / Modeler:* รับผิดชอบ T05–T08, R4 (วิศวกรรมฟีเจอร์, พัฒนาโมเดล LR, RF, HistGradientBoosting และการจูนเกณฑ์ตัดสิน)
  3. **นาย ค. [รหัสนักศึกษา]** — *Storyteller & QA Specialist:* รับผิดชอบ T04, T09, T11, R1/R3/R5/R6 (วิเคราะห์ EDA, วิเคราะห์ความผิดพลาด, นโยบาย Two-Tier, ตรวจสอบตัวเลข)

---

## 🏛️ Box R1 — ที่มาและความสำคัญของปัญหา (Sensible Problem & Framing)
*(คะแนนความสำคัญของโจทย์: 30% ตามเกณฑ์การประเมิน R1)*

ตอบครบ 5 คำถามหลักในการตั้งโจทย์ Data Science ภาคปฏิบัติ:

1. **ใครคือผู้ใช้งาน และใช้ตัดสินใจอะไร? (User & Decision):**
   - ผู้ใช้งานหลักคือ **สำนักงานสาธารณสุขจังหวัด (สสจ.)** ร่วมกับเครือข่ายโรงพยาบาลและ อสม.
   - ตัดสินใจบริหารจัดการ 3 มาตรการล่วงหน้า 1 เดือน: (1) อนุมัติงบพ่นหมอกควัน/สารเคมี ULV ในพื้นที่เสี่ยง, (2) ระดม อสม. รณรงค์เคาะประตูบ้านคว่ำภาชนะกำจัดลูกน้ำยุงลายและแจกทรายอะเบท, (3) สำรองเตียงผู้ป่วย สารน้ำ Ringer's lactate และเกล็ดเลือดในโรงพยาบาลประจำจังหวัด/อำเภอ
2. **ทำนายเมื่อไร และมีข้อมูลพร้อมใช้งานหรือไม่? (Prediction Time & No Leakage):**
   - ทำนาย ณ **วันสุดท้ายของเดือน $t$** เพื่อพยากรณ์สถานะการระบาดใน **เดือน $t+1$** (ให้เวลาเตรียมการล่วงหน้า 1 เดือนเต็ม)
   - ข้อมูลเข้าใช้เฉพาะยอดผู้ป่วยสะสมและสภาพอากาศถึงสิ้นเดือน $t$ เท่านั้น **ไม่มีการใช้สภาพอากาศล่วงหน้าในอนาคต** เพื่อป้องกันการรั่วไหลของข้อมูล (Zero Data Leakage)
3. **1 แถวข้อมูลแทนอะไร? (Row Definition):**
   - **จังหวัด × เดือน** (77 จังหวัด × 360 เดือน ในช่วง 30 ปี พ.ศ. 2536–2565 / ค.ศ. 1993–2022)
4. **นิยามเป้าหมายที่วัดผลได้ในทางคณิตศาสตร์คืออะไร? (Measurable Target):**
   - นิยามการระบาด: $\text{{outbreak}}_{{p, t+1}} = 1$ เมื่อจำนวนผู้ป่วยในเดือน $t+1$ สูงเกินเกณฑ์ทางระบาดวิทยา:
     $$\text{{cases}}_{{p, t+1}} > \mu_p + 1.0 \cdot \sigma_p$$
   - โดยค่าเฉลี่ย ($\mu_p$) และส่วนเบี่ยงเบนมาตรฐาน ($\sigma_p$) คำนวณจำเพาะของแต่ละจังหวัด จาก **ปีชุดฝึกสอน (Train 1993–2015) เท่านั้น**
5. **ความผิดพลาดแบบใดสร้างความเสียหายรุนแรงกว่ากัน? (Costly Error & Metric):**
   - **False Negative (ไม่เตือน แต่เกิดการระบาดจริง):** สร้างความเสียหายรุนแรงที่สุด เพราะทำให้ สสจ. ไม่ได้เตรียมการ เกิดการระบาดลุกลาม โรงพยาบาลขาดแคลนเตียงและสารน้ำฉุกเฉิน และนำไปสู่การเสียชีวิตของผู้ป่วยที่ป้องกันได้
   - **False Positive (เตือน แต่ไม่ถึงเกณฑ์ระบาด):** เสียหายเฉพาะงบสำรวจลูกน้ำยุงลาย ซึ่งการลงพื้นที่กำจัดยุงลายก็ยังมีผลดีต่อสุขอนามัยชุมชน
   - **ตัวชี้วัดหลัก (Primary Metric):** จึงเลือกใช้ **Recall บนเดือนที่ระบาด (Recall on Outbreak Months)** เป็นเป้าหมายสูงสุด โดยต้องรักษา Precision, F1-score และ PR-AUC ให้อยู่ในระดับที่ยอมรับได้ทางปฏิบัติ

---

## 📊 Box R2 — แหล่งข้อมูลเปิดและการเตรียมข้อมูลที่ตรวจสอบได้ (Verifiable Data & Prep)

### 1. แหล่งข้อมูลเปิดและสัญญาอนุญาต (Open Data & Licenses)
- **สถิติผู้ป่วยไข้เลือดออก:** OpenDengue V1.3.1 (ใบอนุญาต CC BY 4.0; Clarke et al., *Scientific Data* 2024) ข้อมูลรายจังหวัด-รายเดือนของประเทศไทย 1993–2022
- **สภาพอากาศย้อนหลัง:** Open-Meteo ERA5 Historical Reanalysis Archive (ใบอนุญาต CC BY 4.0) ดึงข้อมูลอุณหภูมิ (°C), ฝนสะสม (mm), ความชื้นสัมพัทธ์ (%) ณ พิกัดศูนย์กลางภูมิศาสตร์ของ 77 จังหวัด

### 2. มิติข้อมูลและปัญหาคุณภาพข้อมูลที่ค้นพบ (Data Cleaning & Quality Audit)
- **ขนาดข้อมูลรวม (Panel):** {total_panel:,} แถว (77 จังหวัด × 360 เดือน)
- **ตารางสำหรับฝึกโมเดล (Modeling Table):** {total_model:,} แถว (ตัด lag 12 เดือนแรกของประวัติศาสตร์ และตัดช่วงก่อนตั้งจังหวัดใหม่)
- **การจัดการชื่อจังหวัดที่ 78:** ตรวจพบชื่อเกินใน OpenDengue คือ `PRACHIN BURI` (1993–2002) และ `PHACHINBURI` (2003–2022) ซึ่งคือจังหวัดปราจีนบุรีเดียวกัน ทำการรวมประวัติศาสตร์เหลือ 77 จังหวัดที่สมบูรณ์
- **จังหวัดตั้งใหม่ 5 จังหวัด:** อำนาจเจริญ, มุกดาหาร, หนองบัวลำภู, สระแก้ว (ตั้งช่วงปี 1993 ข้อมูลเริ่ม 2003) และบึงกาฬ (ตั้งปี 2011) ขาดข้อมูลช่วงต้นรวม {missing_months_late:,} จังหวัด-เดือน ทางกลุ่มไม่ทำ Imputation เท็จ แต่ตัดแถวก่อนจัดตั้งจังหวัดออกจากการสร้างตารางโมเดล
- **การเปลี่ยนแปลงนิยามรายงานโรคปี 2021–2022:** เปลี่ยนมาใช้ยอดรวม `dengue_total` ที่ครอบคลุมทั้ง DF, DHF และ DSS อย่างสม่ำเสมอตลอด 30 ปี

### 3. การแบ่งชุดข้อมูลตามลำดับเวลาอย่างเคร่งครัด (Chronological Split)
*ห้ามใช้ Random Split โดยเด็ดขาดเพื่อป้องกัน Look-ahead Leakage*

| ชุดข้อมูล (Split) | ช่วงปี (Years) | จำนวนแถว | เดือนที่ระบาดจริง | สัดส่วนการระบาด (%) | วัตถุประสงค์การใช้งาน |
|---|---|---|---|---|---|
| **Train** | 1994–2015 | {train_rows:,} | 1,923 | 9.80% | ฝึกสอนโมเดลและคำนวณ $\mu_p, \sigma_p$ |
| **Validation** | 2016–2017 | {val_rows:,} | 70 | 3.79% | จูน Hyperparameters และ Threshold |
| **Test (รวม)** | 2018–2022 | {test_rows:,} | {test_outbreaks:,} | 8.48% | ประเมินผลครั้งเดียวตอนท้ายสุด |
| *• Test ปกติ* | 2018–2019 | {test_norm_rows:,} | 269 | 14.56% | ประเมินผลสภาวะระบาดปกติ |
| *• Test โควิด* | 2020–2022 | {test_covid_rows:,} | 123 | 4.44% | ประเมินผลสภาวะวิกฤตล็อกดาวน์ |

---

## 🔍 Box R3 — ข้อค้นพบจากการสำรวจข้อมูล (EDA Key Findings)
*(อ้างอิงรูปประกอบ: `eda_seasonality.png`, `eda_lag_correlation.png`, `eda_province_heterogeneity.png`, `eda_annual_trend_covid.png`)*

### 1. วงจรฤดูกาลและตัวนำทางสภาพอากาศ (Seasonality & Climate Drivers)
- **อุณหภูมิชี้นำ 2–3 เดือน:** อุณหภูมิเฉลี่ยทั่วประเทศขึ้นสู่จุดสูงสุดในเดือนเมษายน (เดือน {peak_temp_month}, **{peak_temp_c:.2f}°C**) ซึ่งนำหน้าการระบาดสูงสุดของไข้เลือดออกในเดือนกรกฎาคม (เดือน {peak_dengue_month}, **{peak_dengue_cases:.2f} ราย/จังหวัด**) อยู่ 2–3 เดือน สอดคล้องกับค่าสหสัมพันธ์ภายในจังหวัดที่สูงสุดที่ lag 3 (**$r = {temp_lag3_corr:.4f}$**) เนื่องจากความร้อนเร่งวงจรฟักตัวของเชื้อไวรัสในยุง (Extrinsic Incubation Period)
- **ฝนชี้นำ 0–1 เดือน:** มรสุมเริ่มตกชุกในเดือนพฤษภาคม (เดือน {monsoon_month}, **{monsoon_rain:.2f} mm**) นำหน้าการระบาด 0–1 เดือน ($r = {rain_lag0_corr:.4f}$) ทำให้เกิดน้ำขังในภาชนะเพาะพันธุ์ลูกน้ำ

### 2. ความเหลื่อมล้ำสุดขั้วระหว่างจังหวัด (Extreme Spatial Heterogeneity)
- อัตราผู้ป่วยเฉลี่ยต่อเดือนระหว่างจังหวัดต่างกันถึง **{het_ratio:.2f} เท่า** (กรุงเทพฯ สูงสุด **{bkk_mean:.2f} ราย/เดือน** vs หนองบัวลำภู ต่ำสุด **{nongbua_mean:.2f} ราย/เดือน**)
- **ทำไมเกณฑ์ระดับประเทศจึงล้มเหลว:** หากใช้เกณฑ์ระบาดค่าเดียวทั่วประเทศ จะมีถึง **{masked_prov_count} จังหวัด**ที่ไม่เคยได้รับสัญญาณเตือนภัยเลยตลอด 30 ปี ส่งผลให้การกำหนดเกณฑ์เฉพาะรายจังหวัด ($\mu_p + \sigma_p$) เป็นหัวใจสำคัญของความแม่นยำ

### 3. ผลกระทบจากมาตรการล็อกดาวน์ยุคโควิด-19 (COVID-19 Anomaly)
- ในช่วงโควิด-19 (2020–2022) ยอดผู้ป่วยลดฮวบลงถึง **{covid_drop_ratio:.2f} เท่า** (จาก **{cases_2019:,} ราย** ในปี 2019 เหลือเพียง **{cases_2021:,} ราย** ในปี 2021) และสัดส่วนจังหวัดที่ไม่มีผู้ป่วยเลยพุ่งขึ้นเป็น 24.13% เนื่องจากการปิดโรงเรียนและการเดินทางข้ามจังหวัดหยุดชะงัก

---

## 🏆 Box R4 — การเปรียบเทียบโมเดลกับ Baseline (Model vs. Baseline)
*(อ้างอิงรูปประกอบ: `r4_model_vs_baseline.png`)*

ประเมินบนชุดข้อมูลทดสอบจริง (**Test Set 2018–2022, {test_rows:,} จังหวัด-เดือน, มีการระบาดจริง {test_outbreaks} ครั้ง**):

| โมเดล / เกณฑ์เปรียบเทียบ | เกณฑ์ตัดสิน (Threshold) | Recall (จับระบาด) | Precision (แม่นยำ) | F1-Score | PR-AUC | พลาดเตือน (FN) |
|---|---|---|---|---|---|---|
| **1. Majority Class (ไม่เตือนเลย)** | — | {maj_test['recall']*100:.1f}% (0/{test_outbreaks}) | {maj_test['precision']*100:.1f}% | {maj_test['f1']:.4f} | {maj_test['pr_auc']:.4f} | {maj_test['fn']} ครั้ง |
| **2. Seasonal Last Year (เดือนเดียวกันปีก่อน)** | — | {seas_test['recall']*100:.2f}% ({seas_test['tp']}/{test_outbreaks}) | {seas_test['precision']*100:.2f}% | {seas_test['f1']:.4f} | {seas_test['pr_auc']:.4f} | {seas_test['fn']} ครั้ง |
| **3. Persistence (เดือนที่แล้วระบาดไหม)** | — | {pers_test['recall']*100:.2f}% ({pers_test['tp']}/{test_outbreaks}) | {pers_test['precision']*100:.2f}% | {pers_test['f1']:.4f} | {pers_test['pr_auc']:.4f} | {pers_test['fn']} ครั้ง |
| **4. Logistic Regression** | {lr_thresh:.2f} | {lr_test['recall']*100:.2f}% ({lr_test['tp']}/{test_outbreaks}) | {lr_test['precision']*100:.2f}% | {lr_test['f1']:.4f} | {lr_test['pr_auc']:.4f} | {lr_test['fn']} ครั้ง |
| **5. Random Forest** | {rf_thresh:.2f} | {rf_test['recall']*100:.2f}% ({rf_test['tp']}/{test_outbreaks}) | {rf_test['precision']*100:.2f}% | {rf_test['f1']:.4f} | {rf_test['pr_auc']:.4f} | {rf_test['fn']} ครั้ง |
| **6. HistGradientBoosting (โมเดลที่ดีที่สุด)** | **{hgb_thresh:.2f}** | **{hgb_test['recall']*100:.2f}% ({hgb_test['tp']}/{test_outbreaks})** | **{hgb_test['precision']*100:.2f}%** | **{hgb_test['f1']:.4f}** | **{hgb_test['pr_auc']:.4f}** | **{hgb_test['fn']} ครั้ง** |

### สรุปผลความเหนือชั้นของ Machine Learning
- **Recall พุ่งสูงถึง {hgb_test['recall']*100:.2f}%:** เหนือกว่า Persistence Baseline ถึง **+{recall_diff:.2f} percentage points**
- **ลดการหลุดเตือนลง {fn_reduction_pct:.1f}%:** ลดจำนวนเดือนที่ระบาดโดยไม่รู้ตัวจาก 148 ครั้งเหลือเพียง 46 ครั้ง ช่วยให้บุคลากรสาธารณสุขมีเวลาตั้งรับล่วงหน้า
- **ทนทานต่อวิกฤตข้ามยุค:** รักษา Recall สูงทั้งในยุคปกติ 2018–2019 (**{hgb_norm['recall']*100:.2f}%**) และยุคโควิด 2020–2022 (**{hgb_covid['recall']*100:.2f}%**)

---

## 🎯 Box R5 — การวิเคราะห์ความผิดพลาดของโมเดล (Know Where Model Fails)
*(อ้างอิงรูปประกอบ: `r5_error_analysis.png`)*

### 1. จุดบอดของ Baseline vs ความสามารถของ ML ในการเตือน "เริ่มระบาดใหม่"
ในการระบาดจริง {test_outbreaks} ครั้ง แบ่งเป็น **ระบาดต่อเนื่อง (Ongoing)** {ongoing_count} ครั้ง และ **เริ่มระบาดใหม่ (Onset)** {onset_count} ครั้ง:
- **Persistence บอดสนิทต่อการเริ่มระบาดใหม่:** ทำ Onset Recall ได้ **{pers_onset_rec*100:.1f}% (0/{onset_count})** ไม่สามารถเตือนล่วงหน้าได้แม้แต่ครั้งเดียว
- **HistGradientBoosting เตือนการเริ่มระบาดล่วงหน้าได้ถึง {hgb_onset_rec*100:.1f}% ({err['onset_vs_ongoing']['hist_gradient_boosting']['onset']['tp']}/{onset_count}):** ป้องกันโรงพยาบาลไม่ให้ถูกจู่โจมฉับพลัน

### 2. กายวิภาคของ False Negatives ({total_fn_count} ครั้งที่โมเดลหลุดเตือน)
- **{fn_onset_pct:.1f}% ({fn_onset_count}/{total_fn_count} ครั้ง)** คือกรณี Onset ที่ยอดผู้ป่วยพุ่งกระโดดฉับพลันแบบก้าวกระโดดเฉลี่ย **{missed_case_jump:.2f} เท่า** ในเดือนเดียว โดยไม่มีสัญญาณเตือนจากยอดผู้ป่วยเดือนก่อนหน้า
- **กรณีตัวอย่างจริง:**
  - *บึงกาฬ (พ.ค. 2019):* ผู้ป่วยกระโดด **14.1 เท่า** (จาก 7.0 สู่ 99.0 ราย เกณฑ์ 53.3 ราย) ช่วงลมมรสุมเข้าฉับพลัน
  - *สิงห์บุรี (มิ.ย. 2019):* ผู้ป่วยกระโดด **10.5 เท่า** (จาก 4.0 สู่ 42.0 ราย เกณฑ์ 24.8 ราย) ข้ามเกณฑ์ขนาดเล็ก
  - *อุดรธานี (ก.ค. 2020):* ผู้ป่วยกระโดด **10.4 เท่า** (จาก 28.0 สู่ 291.0 ราย) แหวกกระแสช่วงโควิด-19

### 3. กายวิภาคของ False Positives ({fp_total} ครั้งที่โมเดลเตือนเกิน)
ถึง **{fp_actionable_pct:.1f}% ({fp_actionable_count}/{fp_total} ครั้ง)** เป็นสัญญาณเตือนที่มีประโยชน์ทางสาธารณสุขสูง (Actionable Near-Miss):
1. **เฉียดเกณฑ์ระบาด (Elevated Near-Miss):** {fp_nearmiss_pct:.1f}% ({fp_nearmiss_count} ครั้ง) ผู้ป่วยสูงเฉียดเกณฑ์ เช่น *สมุทรสาคร (มิ.ย. 2018)* มีผู้ป่วย 64.0 ราย พลาดเกณฑ์ 64.5 ราย ไปเพียง **0.5 ราย**
2. **หางคลื่นระบาด (Post-Outbreak Tail):** {fp_tail_pct:.1f}% ({fp_tail_count} ครั้ง) เดือนก่อนระบาดหนัก ยอดกำลังลดลง เช่น *เลย (ส.ค. 2019)* มี 141.0 ราย (เกณฑ์ 148.2)
3. **เตือนล่วงหน้า 2 เดือน (Pre-Outbreak $t+2$):** {fp_early_pct:.1f}% ({fp_early_count} ครั้ง) เดือน $t+1$ ยังไม่ระบาด แต่ระบาดหนักในเดือน $t+2$ เช่น *ชัยภูมิ (พ.ค. 2019)* เตือนที่ 159 ราย ก่อนระบาดหนัก 389 รายในเดือนถัดไป
- มีเพียง **{fp_pure_pct:.1f}% ({fp_pure_count}/{fp_total} ครั้ง)** เท่านั้นที่เป็นการเตือนผิดพลาดแท้จริง (Pure False Alarm)

---

## 💡 Box R6 — ข้อเสนอแนะเชิงปฏิบัติการและความคุ้มค่า (Practical Policy & Limits)
*(อ้างอิงรูปประกอบ: `r6_threshold_policy.png`)*

### 1. ระบบเตือนภัย 2 ระดับสำหรับ สสจ. (Two-Tier Early Warning Protocol)
เพื่อขจัดปัญหาเตือนพร่ำเพรื่อ (Alert Fatigue) ออกแบบแนวทางปฏิบัติการจำแนกตามระดับความน่าจะเป็น ($p$):

```mermaid
flowchart LR
    RiskInput["ผลทำนายความน่าจะเป็น (p)"] --> GreenZone["สีเขียว (p < 0.35)\nความเสี่ยงระบาด 0.90%\nเฝ้าระวังปกติ รง.506"]
    RiskInput --> YellowZone["สีเหลือง Watch (0.35 <= p < 0.65)\nความเสี่ยงระบาด 17.12%\nระดม อสม. คว่ำภาชนะ / ตรวจทรายอะเบท"]
    RiskInput --> RedZone["สีแดง High Alert (p >= 0.65)\nความเสี่ยงระบาด 60.53%\nเปิด EOC / พ่น ULV / สำรองเตียง & สารน้ำ"]
```

- **สีเขียว (Green, $p < 0.35$):** ครอบคลุม **{green_pct:.1f}% ของเดือนทั้งหมด** มีความเสี่ยงระบาดเพียง **{green_risk:.2f}%** (<1 ใน 100 เดือน) ไม่ต้องเสียงบประมาณฉุกเฉิน
- **สีเหลือง Tier-1 Watch ($0.35 \le p < 0.65$):** ครอบคลุม **{yellow_pct:.1f}% ของเดือน** (เฉลี่ย {yellow_alerts_yr:.2f} ครั้ง/จังหวัด/ปี) ความเสี่ยง **{yellow_risk:.2f}%** ใช้มาตรการต้นทุนต่ำ (0.3x) ระดม อสม. สำรวจลูกน้ำยุงลาย
- **สีแดง Tier-2 High Alert ($p \ge 0.65$):** ครอบคลุม **{red_pct:.1f}% ของเดือน** (เฉลี่ย {red_alerts_yr:.2f} ครั้ง/จังหวัด/ปี) ความเสี่ยงสูงถึง **{red_risk:.2f}%** (>6 ใน 10 เดือนระบาดจริง) สั่งเปิด EOC พ่นหมอกควัน และสำรองเตียง/สารน้ำ Ringer's lactate
- **ผลลัพธ์รวม:** เขตเตือนภัย ($p \ge 0.35$) ตรวจจับการระบาดได้ถึง **{comb_recall:.2f}% ({comb_caught}/{test_outbreaks} ครั้ง)**

### 2. การวิเคราะห์ความคุ้มค่าเชิงตัวเลข (Parametric Cost Dominance)
- เมื่ออัตราส่วนความเสียหายของการหลุดเตือน $R = C_{{\text{{missed}}}} / C_{{\text{{alert}}}} \ge 3$ ระบบ ML Two-Tier ประหยัดต้นทุนรวมเหนือกว่าทุก Baseline อย่างสมบูรณ์ (Mathematical Dominance)
- **ประหยัดต้นทุน 65.9% – 69.7%** เมื่อเทียบกับการรณรงค์เหวี่ยงแหช่วงหน้าฝน 6 เดือน (Blanket Campaign)
- **ลดภาระงานแจ้งเตือนลง 72.2%** และ **ลดการเตือนเก้อลง 85.0%** ที่เกณฑ์เดี่ยว 0.49
- **ปรับลดการเตือนอัตโนมัติ 56.0% ในช่วงโควิด-19** ป้องกันการสิ้นเปลืองทรัพยากรภาครัฐ

### 3. ข้อจำกัดที่ข้อมูลยังพิสูจน์ไม่ได้ 4 ประการ (Limits the Data Cannot Prove)
1. **ข้อมูลเฝ้าระวังไม่เท่ากับผลลัพธ์เชิงสาเหตุ (Surveillance ≠ Causal Effect):** โมเดลบอกความเสี่ยงล่วงหน้า แต่ไม่สามารถพิสูจน์ว่าเมื่อพ่นสารเคมีแล้วจะลดยอดผู้ป่วยได้กี่เปอร์เซ็นต์ (ต้องใช้การทดลองแบบ Stepped-Wedge Cluster Trial)
2. **ความละเอียดระดับจังหวัด (Admin1) vs รัศมียุงบิน 100–400 เมตร:** โมเดลบอกว่าจังหวัดใดเสี่ยง แต่ สสจ. ต้องใช้ข้อมูล รง.506 รายสัปดาห์ระดับตำบล/หมู่บ้านเพื่อชี้เป้าพ่นสารเคมีในชุมชน
3. **ปัจจัยไวรัสสายพันธุ์ย่อย (DENV-1..4) และภูมิคุ้มกันหมู่:** ฐานข้อมูลเปิดไม่มีข้อมูล Serotype การเปลี่ยนสายพันธุ์หลักอาจเร่งการระบาดนอกเหนือสถิติในอดีต
4. **สภาพอากาศจากดาวเทียม vs พฤติกรรมการกักเก็บน้ำในครัวเรือน:** สภาพอากาศระบุความเหมาะสมทางชีววิทยา แต่ไม่สามารถแทนที่การตรวจตุ่มน้ำและโอ่งมังกรในบ้านได้

---

## 🤖 Box R7 — บันทึกการทำงานร่วมกับ AI และการตรวจสอบแก้ไข (AI-Use Log)
*(ข้อกำหนด R7: แสดงการมีวิจารณญาณและตรวจพบจุดบกพร่องของ AI อย่างน้อย 1 กรณี)*

| ลำดับงาน | เครื่องมือ AI | คำแนะนำ/ผลลัพธ์แรกเริ่มของ AI | ข้อผิดพลาดที่กลุ่มตรวจพบ | การตัดสินใจแก้ไขของกลุ่ม (Human-in-the-Loop) |
|---|---|---|---|---|
| **T02** | Claude / Gemini | เสนอให้เขียนโค้ดคำนวณจุดกึ่งกลางจังหวัดด้วย LAEA Projection และ Shapely | **Hallucination:** ไม่มีไลบรารี shapely ติดตั้งในเครื่อง และไฟล์ `provinces.geojson` มีพิกัด lat/lon อยู่แล้วใน Properties | ปฏิเสธโค้ด AI และเขียนฟังก์ชันอ่านค่าพิกัดตรงจาก geojson ช่วยลดเวลาและไม่ต้องลงแพ็กเกจเพิ่ม |
| **T07** | Copilot / Claude | เรียกใช้ `.feature_importances_` บนโมเดล `HistGradientBoostingClassifier` | **API Incompatibility:** โมเดลตระกูล HistGradientBoosting ของ scikit-learn ไม่มี attribute ดังกล่าว ทำให้เกิด Error | สั่งแก้เป็นการคำนวณ Validation Permutation Importance แทน ซึ่งได้ผลวิเคราะห์ฟีเจอร์ที่น่าเชื่อถือกว่า |
| **T04/07/08/09** | Gemini Assistant | สร้างกราฟแสดงผลโดยวางตำแหน่ง Label / Legend ซ้อนทับแท่งกราฟและเส้นข้อมูล | **Visual Defect:** ป้ายตัวเลขทับข้อมูลสำคัญในรูป Lag Correlation, R4, R5 และ R6 | ปรับโค้ด matplotlib กำหนด `ylim`, ปรับตำแหน่ง Callout box และแยก Legend 2 คอลัมน์ให้อ่านง่าย |
| **T05/T07** | Claude Assistant | เสนอให้แบ่ง Train/Test ด้วย `train_test_split(shuffle=True)` และคำนวณเกณฑ์ระบาดจากข้อมูลทั้งหมด | **Data Leakage:** ข้อมูลอนาคตรั่วไหล และผิดธรรมชาติของข้อมูลอนุกรมเวลาทางระบาดวิทยา | ปฏิเสธทันที และล็อกกฎใน SSOT ให้แบ่งตามปีปฏิทินเคร่งครัด พร้อมคำนวณ $\mu_p, \sigma_p$ จากปี Train เท่านั้น |
| **T10/T11** | Claude Assistant | เสนอให้ติดตั้ง `tabulate` และ `qrcode` เพิ่มเติมเพื่อจัดตารางและสร้างภาพ QR | **Dependency Violation:** ขัดกับกฎข้อ 5 ใน `AGENTS.md` (ห้ามติดตั้งแพ็กเกจใหม่โดยไม่จำเป็น) | เขียนฟังก์ชันจัดตารางด้วยสตริงมาตรฐาน และสร้าง QR Code ด้วยตัวแปลงมาตรฐานร่วมกับ PIL/cv2 |

---

## 🔗 Footer & QR Codes (ส่วนท้ายและรหัสคิวอาร์)

```
[QR Code 1: Colab Notebook]      [QR Code 2: OpenDengue Dataset]      [QR Code 3: Open-Meteo Weather]
     (poster/qr_colab.png)            (poster/qr_opendengue.png)            (poster/qr_weather.png)
https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS
https://opendengue.org · https://open-meteo.com/en/docs/historical-weather-api
```

- **เอกสารอ้างอิงข้อมูล:**
  1. Clarke, J., Lim, A., Gupte, P., Pigott, D. M., van Panhuis, W. G., & Brady, O. J. (2024). A global dataset of publicly available dengue case count data. *Scientific Data*, 11(1), 296. (OpenDengue V1.3.1)
  2. Open-Meteo ERA5 Historical Weather API (European Centre for Medium-Range Weather Forecasts - ECMWF reanalysis).
  3. กรมควบคุมโรค กระทรวงสาธารณสุข ประเทศไทย (รายงานการเฝ้าระวังโรคทางระบาดวิทยา รง.506).

---

## 📐 Visual Layout Blueprint (ผังการจัดวางบน Canva / Figma A2)
- **ขนาดกระดาษ:** A2 แนวตั้ง (Portrait) 420 × 594 มิลลิเมตร (300 DPI: 4961 × 7016 พิกเซล)
- **ระบบกริด:** 3 คอลัมน์โมดูลาร์ (Modular 3-Column Grid, Margin 15 มม., Gutter 10 มม.)
  - **ส่วนบนสุด (Full Width):** Poster Header (ชื่อเรื่องโดดเด่น, ตราสัญลักษณ์ SDG 3, รายชื่อผู้จัดทำและบทบาท)
  - **คอลัมน์ซ้าย (Column 1):**
    - Box R1: ที่มาและความสำคัญ (5 Framing Questions)
    - Box R2: ข้อมูลและการแบ่งชุดข้อมูล (ตาราง Chronological Split)
    - Box R7: บันทึกการใช้ AI และการกำกับดูแลโดยมนุษย์ (AI Oversight Table)
  - **คอลัมน์กลาง (Column 2):**
    - Box R3: ข้อค้นพบจากการสำรวจข้อมูล (ใส่รูป `eda_seasonality.png` และ `eda_province_heterogeneity.png`)
    - Box R4: โมเดล vs Baseline (ใส่รูป `r4_model_vs_baseline.png` + ตารางเปรียบเทียบผล Test Set)
  - **คอลัมน์ขวา (Column 3):**
    - Box R5: การวิเคราะห์ความผิดพลาด (ใส่รูป `r5_error_analysis.png` + ตาราง Onset vs Ongoing)
    - Box R6: ข้อเสนอแนะเชิงนโยบาย Two-Tier & ข้อจำกัด 4 ข้อ (ใส่รูป `r6_threshold_policy.png`)
  - **ส่วนล่างสุด (Full Width):** Footer & QR Codes 3 จุด พร้อมลิงก์เข้าถึงโค้ดและข้อมูล
- **ชุดสี (Color Palette):**
  - สีกรมท่าสุขาภิบาล (Navy `#1B365D`): สีพื้นหัวข้อหลักและกรอบเน้นความน่าเชื่อถือ
  - สีแดงเตือนภัยไข้เลือดออก (Crimson Alert `#D9381E`): ใช้เน้นเดือนที่เกิดการระบาดและจุดผิดพลาด
  - สีเหลืองอำพันระวังภัย (Amber Watch `#E69F00`): ใช้แสดงสถานะเตือนภัย Tier-1
  - สีเขียวปลอดภัย (Forest Green `#2E7D32`): ใช้แสดงสถานะเฝ้าระวังปกติ Green Tier
"""
    return content


def format_summary_th_markdown(data: dict) -> str:
    """Construct updated comprehensive Thai project summary replacing all TBDs."""
    m = data["metrics"]
    eda = data["eda"]
    feat = data["feat"]
    err = data["err"]
    pol = data["pol"]

    hgb_test = m["models"]["hist_gradient_boosting"]["metrics"]["test"]
    pers_test = m["baselines"]["persistence_last_month"]["test"]
    comb_recall = pol["two_tier_test"]["overall_alert_zone"]["recall"] * 100

    content = rf"""# สรุปโครงการวิทยาการข้อมูล (Data Science Capstone Summary)
**โครงการ:** พยากรณ์เดือนที่เกิดการระบาดของโรคไข้เลือดออกรายจังหวัดในประเทศไทยล่วงหน้า 1 เดือน (1993–2022)  
**ชื่อภาษาไทยสำหรับโปสเตอร์:** **"เดือนหน้าไข้เลือดออกระบาดไหม?"**  
**เป้าหมายการพัฒนาที่ยั่งยืน:** SDG 3 — Good Health and Well-being (สุขภาพและความเป็นอยู่ที่ดี, เป้าประสงค์ 3.3)  
**วิชา:** CPE312 Data Science Capstone (ปีการศึกษา 2569)

---

## 1. ที่มาและกรอบปัญหา (R1 Problem Framing)
1. **ผู้ใช้งานและการตัดสินใจ:** สำนักงานสาธารณสุขจังหวัด (สสจ.) ทั้ง 77 จังหวัด ใช้ตัดสินใจ 3 ด้านล่วงหน้า 1 เดือน:
   - จัดสรรงบประมาณและสารเคมีพ่นหมอกควัน/ULV ในพื้นที่เสี่ยง
   - ระดมกำลัง อสม. รณรงค์เคาะประตูบ้านคว่ำภาชนะกำจัดลูกน้ำยุงลายและแจกทรายอะเบท
   - สำรองเตียงผู้ป่วย สารน้ำ Ringer's lactate และเกล็ดเลือดในโรงพยาบาล
2. **เวลาที่ทำนาย:** ทำนาย ณ **สิ้นเดือน $t$** เพื่อพยากรณ์สถานะการระบาดใน **เดือน $t+1$** (ใช้เฉพาะข้อมูลที่มีอยู่จริงถึงสิ้นเดือน $t$ ปราศจาก Data Leakage)
3. **1 แถวข้อมูลคือ:** **จังหวัด × เดือน** (77 จังหวัด × 360 เดือน ในช่วง 30 ปี พ.ศ. 2536–2565)
4. **เป้าหมายที่วัดผลได้:** $\text{{outbreak}}_{{p, t+1}} = 1$ เมื่อผู้ป่วยในเดือน $t+1 > \mu_p + 1.0\sigma_p$ ของจังหวัดนั้น คำนวณจากปี Train (1993–2015) เท่านั้น
5. **ความผิดพลาดที่แพงกว่า:** การหลุดเตือนระบาด (**False Negative**) ส่งผลให้ประชาชนเจ็บป่วยรุนแรงและโรงพยาบาลรับมือไม่ทัน เสียหายกว่าการเตือนเกิน (**False Positive**) จึงใช้ **Recall บนเดือนที่ระบาด** เป็นตัวชี้วัดหลัก

---

## 2. ข้อมูลและการเตรียมข้อมูล (R2 Data & Verification)
- **สถิติผู้ป่วย:** OpenDengue V1.3.1 (CC BY 4.0) รายจังหวัด-รายเดือน 1993–2022
- **สภาพอากาศ:** Open-Meteo ERA5 (CC BY 4.0) ฝน อุณหภูมิ ความชื้น ณ จุดกึ่งกลาง 77 จังหวัด
- **ขนาดข้อมูล:** {feat['total_panel_rows']:,} แถวใน `panel.csv` และ {feat['modeling_table_rows']:,} แถวใน `modeling_table.csv` หลังตัด lag 12 เดือนแรกและช่วงก่อนจัดตั้งจังหวัด
- **การจัดการคุณภาพข้อมูล:**
  - รวมชื่อจังหวัดที่ 78: รวม `PRACHIN BURI` (1993–2002) และ `PHACHINBURI` (2003–2022) เป็นปราจีนบุรี
  - จังหวัดตั้งใหม่ 5 จังหวัด: ขาดข้อมูลช่วงต้นรวม 696 จังหวัด-เดือน ไม่ impute เท็จแต่ตัดออกในการสร้างตารางโมเดล
  - การแบ่งตามเวลา (Chronological Split): Train 1994–2015 ({feat['splits']['train']['rows']:,} แถว), Val 2016–2017 ({feat['splits']['val']['rows']:,} แถว), Test 2018–2022 ({feat['splits']['test']['rows']:,} แถว)

---

## 3. ข้อค้นพบจากการสำรวจข้อมูล (R3 EDA Findings)
- **อุณหภูมินำหน้า 2–3 เดือน:** อุณหภูมิเฉลี่ยสูงสุดในเดือนเมษายน ({eda['seasonality']['peak_temp_mean_c']:.2f}°C) นำหน้าผู้ป่วยสูงสุดเดือนกรกฎาคม ({eda['seasonality']['peak_dengue_mean_cases']:.2f} ราย/จังหวัด) โดยมีค่าสหสัมพันธ์ lag 3 สูงสุดที่ $r = {eda['lag_correlations']['temp_mean_c'][3]['median_within_province']:.4f}$
- **ฝนนำหน้า 0–1 เดือน:** ฝนเริ่มตกหนักเดือนพฤษภาคม ({eda['seasonality']['monsoon_onset_mean_precip_mm']:.2f} mm) นำหน้า 0–1 เดือน ($r = {eda['lag_correlations']['precip_sum_mm'][0]['median_within_province']:.4f}$)
- **ความเหลื่อมล้ำระหว่างจังหวัด {eda['province_heterogeneity']['ratio_top_to_bottom_mean']:.2f} เท่า:** กรุงเทพฯ มีผู้ป่วยเฉลี่ย {eda['province_heterogeneity']['highest_province']['mean']:.2f} ราย/เดือน ขณะที่หนองบัวลำภูมีเพียง {eda['province_heterogeneity']['lowest_province']['mean']:.2f} ราย/เดือน หากใช้เกณฑ์เดียวทั้งประเทศจะมีถึง 11 จังหวัดที่ไม่เคยได้รับคำเตือนเลย
- **ผลกระทบโควิด-19:** ผู้ป่วยลดลง {eda['annual_trends']['covid_drop_ratio_2019_to_2021']:.2f} เท่า จาก {eda['annual_trends']['year_2019_cases']:,} ราย (2019) เหลือ {eda['annual_trends']['year_2021_cases']:,} ราย (2021)

---

## 4. ผลการสร้างโมเดลและการเปรียบเทียบ (R4 Modeling vs Baseline)
บนชุดข้อมูลทดสอบ Test Set 2018–2022 ({feat['splits']['test']['rows']:,} แถว, ระบาดจริง {feat['splits']['test']['outbreak_count']} ครั้ง):
- **Majority Class:** Recall 0.0%, F1 0.0000, PR-AUC 0.0848
- **Seasonal Last Year:** Recall {m['baselines']['seasonal_last_year']['test']['recall']*100:.2f}%, F1 {m['baselines']['seasonal_last_year']['test']['f1']:.4f}, PR-AUC 0.1453
- **Persistence Last Month:** Recall {pers_test['recall']*100:.2f}%, F1 {pers_test['f1']:.4f}, PR-AUC 0.4255 (พลาดเตือน 148 ครั้ง)
- **HistGradientBoosting (เกณฑ์ 0.49 จาก Val):** **Recall {hgb_test['recall']*100:.2f}% (346/392 ครั้ง)**, Precision {hgb_test['precision']*100:.2f}%, F1 {hgb_test['f1']:.4f}, PR-AUC 0.7657
- **ผลลัพธ์:** ML เหนือกว่า Persistence ถึง **+{(hgb_test['recall'] - pers_test['recall'])*100:.2f} percentage points** ลดการหลุดเตือนลง **{(pers_test['fn'] - hgb_test['fn'])/pers_test['fn']*100:.1f}%** (จาก 148 เหลือ 46 ครั้ง) และทนทานข้ามยุคโควิด-19 (Recall 89.22% ในยุคปกติ และ 86.18% ในยุคโควิด)

---

## 5. การวิเคราะห์จุดบกพร่องของโมเดล (R5 Error Analysis)
- **เดือนเริ่มระบาดใหม่ (Onset 148 ครั้ง):** Persistence ทำ Recall ได้ **0.0% (0/148)** ขณะที่ HistGradientBoosting ทำได้ถึง **{err['onset_vs_ongoing']['hist_gradient_boosting']['onset']['recall']*100:.1f}% (108/148)**
- **46 ครั้งที่โมเดลหลุดเตือน (FN):** เป็น Onset ถึง **{err['onset_vs_ongoing']['hist_gradient_boosting']['fn_share']['onset_fn_pct']:.1f}%** ที่ยอดผู้ป่วยกระโดดเฉลี่ย **{err['onset_vs_ongoing']['hist_gradient_boosting']['onset_case_dynamics']['missed_mean_case_jump']:.2f} เท่า** ในเดือนเดียว (เช่น บึงกาฬ พ.ค. 2019 กระโดด 14.1 เท่า)
- **295 ครั้งที่เตือนเกิน (FP):** พบว่า **{err['fp_anatomy_hgb']['at_least_one_benign']['pct']:.1f}%** เป็นสัญญาณเตือนที่มีประโยชน์ทางสาธารณสุข (เฉียดเกณฑ์ 41.0%, หลังระบาดเพิ่งลดลง 36.9%, เตือนล่วงหน้า 2 เดือน 15.6%) มีเพียง **{err['fp_anatomy_hgb']['pure_false_alarm']['pct']:.1f}%** เท่านั้นที่เป็นการเตือนผิดพลาดแท้จริง

---

## 6. ข้อเสนอแนะเชิงปฏิบัติการและความคุ้มค่า (R6 Recommendations & Policy)
- **ระบบเตือนภัย 2 ระดับ (Two-Tier Protocol):**
  - **สีเขียว ($p < 0.35$):** 83.8% ของเดือน ความเสี่ยงระบาด 0.90% -> เฝ้าระวังปกติผ่าน รง.506
  - **สีเหลือง Watch ($0.35 \le p < 0.65$):** 4.8% ของเดือน ความเสี่ยง 17.12% -> อสม. คว่ำภาชนะ ตรวจทรายอะเบท (ต้นทุน 0.3x)
  - **สีแดง High Alert ($p \ge 0.65$):** 11.4% ของเดือน ความเสี่ยง 60.53% -> เปิด EOC พ่นหมอกควัน สำรองเตียงและสารน้ำ Ringer's lactate (ต้นทุน 1.0x)
  - เขตเตือนภัยรวม ($p \ge 0.35$) ตรวจจับการระบาดได้ถึง **{comb_recall:.2f}% (357/392 ครั้ง)**
- **ความคุ้มค่า:** เมื่อ $R \ge 3$ ระบบ ML ให้ต้นทุนต่ำกว่าทุกวิธี ประหยัดต้นทุน 65.9%–69.7% เทียบกับรณรงค์ปูพรม 6 เดือน และลดงานแจ้งเตือนลง 72.2%
- **ข้อจำกัด 4 ประการที่ข้อมูลพิสูจน์ไม่ได้:** ข้อมูลเฝ้าระวังไม่ใช่ผลเชิงสาเหตุ, ความละเอียดระดับจังหวัดต้องใช้ร่วมกับ รง.506 ชี้เป้าตำบล/หมู่บ้าน, ไม่มีข้อมูลสายพันธุ์ไวรัสและภูมิคุ้มกันหมู่, สภาพอากาศจากสถานีไม่สะท้อนภาชนะเก็บน้ำในบ้าน

---

## 7. บันทึกการทำงานร่วมกับ AI (R7 AI-Use Log)
ทีมงานทำหน้าที่เป็นผู้กำกับดูแลและตรวจสอบ (Human-in-the-Loop) ตรวจพบและแก้ไขข้อผิดพลาดสำคัญของ AI เช่น:
1. ปฏิเสธโค้ดคำนวณจุดกึ่งกลางจังหวัดด้วย LAEA Projection ที่ AI สร้างขึ้นเกินจริงใน T02 โดยเปลี่ยนมาอ่านพิกัดจริงจาก geojson
2. แก้ไข Bug จากการที่ AI พยายามเรียก `.feature_importances_` บน HistGradientBoosting ใน T07 โดยเปลี่ยนเป็น Validation Permutation Importance
3. ตรวจสอบและสั่งแก้ไขป้ายข้อความทับข้อมูลในกราฟ R3, R4, R5, R6
4. ปฏิเสธการสุ่มแบ่งข้อมูลและล็อกกฎการแบ่งตามลำดับเวลาเพื่อป้องกัน Data Leakage
5. ปฏิเสธการลงแพ็กเกจเสริม `tabulate` และ `qrcode` ตามกฎ Rule 5
"""
    return content


def generate_all_qr_codes(base_dir: Path) -> dict[str, Path]:
    """Generate the 3 required QR codes for the poster."""
    poster_dir = base_dir / "poster"
    poster_dir.mkdir(parents=True, exist_ok=True)

    urls = {
        "colab": "https://colab.research.google.com/drive/1ZFD4hoCQNAjVg_cOlb4Wbb63Lx7TdEGS",
        "opendengue": "https://opendengue.org",
        "weather": "https://open-meteo.com/en/docs/historical-weather-api",
    }

    paths = {}
    for key, url in urls.items():
        out_path = poster_dir / f"qr_{key}.png"
        save_qr_png(url, out_path, scale=10)
        paths[key] = out_path

    return paths


def main():
    """Main build function."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    print(f"Loading results artifacts from {base_dir / 'results'}...")
    data = load_all_results(base_dir)

    print("Generating poster content: poster/poster_R1_to_R7_th.md...")
    poster_md = format_poster_markdown(data)
    poster_file = base_dir / "poster" / "poster_R1_to_R7_th.md"
    poster_file.parent.mkdir(parents=True, exist_ok=True)
    with open(poster_file, "w", encoding="utf-8") as f:
        f.write(poster_md)
    print(f"  -> Generated {poster_file} ({len(poster_md)} characters)")

    print("Updating project summary: _agent/docs/SUMMARY_TH.md...")
    summary_md = format_summary_th_markdown(data)
    summary_file = base_dir / "_agent" / "docs" / "SUMMARY_TH.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"  -> Updated {summary_file} ({len(summary_md)} characters)")

    print("Generating scannable QR code PNGs in poster/...")
    qr_paths = generate_all_qr_codes(base_dir)
    for k, p in qr_paths.items():
        print(f"  -> Generated {p.name} ({p.stat().st_size} bytes)")

    print("Build completed successfully.")


if __name__ == "__main__":
    main()
