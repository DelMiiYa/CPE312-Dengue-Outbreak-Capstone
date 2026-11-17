# Brief — T11 Poster content in Thai (R1–R7), Thai summary update, and number audit
Status: TODO · Written by: orchestrator · Date: 2026-11-09

## Goal
Generate the complete, publication-ready Thai A2 poster text (`poster/poster_R1_to_R7_th.md`) and updated Thai project summary (`_agent/docs/SUMMARY_TH.md`) via a reproducible script (`src/poster/build_poster_content.py`) that pulls every number directly from `results/*.json`, generates QR code images (`poster/qr_colab.png`, `poster/qr_opendengue.png`, `poster/qr_weather.png` or SVG/matplotlib equivalents), and verifies 100% numerical consistency with a pytest suite (`tests/test_poster_numbers.py`).

## Why
Serves requirement(s): Poster A2 deliverable (`R1`–`R7` + header + QR codes, where every number on the poster must come from code and match the notebook). Depends on: T10.

## Inputs (exact paths)
- `_agent/docs/SSOT.md`
- `_agent/docs/requirements.md`
- `_agent/docs/SUMMARY_TH.md`
- `results/eda_stats.json`
- `results/feature_summary.json`
- `results/metrics.json`
- `results/error_analysis.json`
- `results/policy_analysis.json`
- `_agent/logs/WORKLOG.md`

## Outputs (exact paths)
- `src/poster/build_poster_content.py` — reproducible Python script that reads all JSON artifacts in `results/` and generates `poster/poster_R1_to_R7_th.md` and updates `_agent/docs/SUMMARY_TH.md`.
- `poster/poster_R1_to_R7_th.md` — complete Thai A2 poster content organized box-by-box (`Header`, `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `R7`, `Footer & QR Codes`, and `Visual Layout Blueprint`), ready to copy-paste into Canva / Figma / PowerPoint A2 template.
- `_agent/docs/SUMMARY_TH.md` — updated comprehensive Thai project summary containing all final verified results from T01–T09 (replacing all old `TBD` placeholders).
- `tests/test_poster_numbers.py` — pytest suite verifying that `poster/poster_R1_to_R7_th.md` and `_agent/docs/SUMMARY_TH.md` exist, contain all required sections (`R1`–`R7`), have zero `TBD` or `UNVERIFIED` placeholders, and contain the exact formatted numbers from `results/metrics.json`, `results/eda_stats.json`, `results/error_analysis.json`, and `results/policy_analysis.json`.

## Constraints
- Follow `_agent/AGENTS.md` and `_agent/docs/SSOT.md`. Do **not** edit `_agent/docs/SSOT.md`.
- **Rule 3 (Numbers come from code):** `src/poster/build_poster_content.py` must load the numbers dynamically from `results/metrics.json`, `results/eda_stats.json`, `results/feature_summary.json`, `results/error_analysis.json`, and `results/policy_analysis.json` and format them into the Thai markdown templates. Never hardcode result numbers by hand.
- **Poster Box Structure in `poster/poster_R1_to_R7_th.md` (Thai language, concise bullet points + tables suitable for A2 poster readability):**
  - **Poster Header:**
    - ชื่อโปรเจกต์: **"เดือนหน้าไข้เลือดออกระบาดไหม?"** (*ระบบพยากรณ์การระบาดของโรคไข้เลือดออกล่วงหน้า 1 เดือน รายจังหวัดในประเทศไทย*)
    - เป้าหมายการพัฒนาที่ยั่งยืน: **SDG 3 — Good Health and Well-being** (เป้าประสงค์ 3.3 ยุติการแพร่ระบาดของโรคเขตร้อนที่ถูกละเลยและโรคติดต่อนำโดยแมลง)
    - สมาชิกกลุ่มและบทบาท (3–4 คน พร้อมช่องกรอกชื่อ-รหัสนักศึกษา และหน้าที่รับผิดชอบชัดเจน)
  - **Box R1 — ที่มาและความสำคัญของปัญหา (Sensible Problem / Business Understanding):**
    - ตอบครบ 5 คำถามหลักตามเกณฑ์ให้คะแนน (30%): (1) ผู้ใช้งานและการตัดสินใจ (`สำนักงานสาธารณสุขจังหวัด - สสจ.` เพื่อจัดสรรงบพ่นหมอกควัน อสม. และสำรองเตียง/สารน้ำล่วงหน้า), (2) เวลาที่พยากรณ์ (สิ้นเดือน $t$ พยากรณ์เดือน $t+1$ ล่วงหน้า 1 เดือน โดยใช้เฉพาะข้อมูลที่มีอยู่จริง ณ สิ้นเดือน $t$), (3) 1 แถวข้อมูลคืออะไร (`จังหวัด × เดือน`, 77 จังหวัด × 360 เดือน), (4) เป้าหมายที่วัดผลได้ (`outbreak_t1 = 1` เมื่อผู้ป่วยเดือนหน้า $> \mu_p + 1.0\sigma_p$ ของแต่ละจังหวัดที่คำนวณจากชุด Train `1993–2015` เท่านั้น), (5) ความผิดพลาดใดเสียหายกว่ากัน (การหลุดเตือนระบาด `False Negative` เสียหายกว่าการเตือนเกิน `False Positive` มาก จึงใช้ **Recall บนเดือนที่ระบาด** เป็นตัวชี้วัดหลัก ควบคู่กับ Precision, F1 และ PR-AUC)
  - **Box R2 — ข้อมูลและการเตรียมข้อมูลที่ตรวจสอบได้ (Verifiable Data & Preparation):**
    - แหล่งข้อมูลเปิดและสัญญาอนุญาต (`OpenDengue v1.3` CC BY 4.0 และ `Open-Meteo ERA5 Historical Archive` CC BY 4.0), ขนาดข้อมูล (`27,720` แถวใน `panel.csv`, `26,100` แถวใน `modeling_table.csv` หลังตัด lag 12 เดือนและจังหวัดตั้งใหม่), ปัญหาข้อมูลที่พบและการจัดการ (การรวมชื่อจังหวัดที่ 78 `PRACHIN BURI` + `PHACHINBURI` เป็นปราจีนบุรี, จังหวัดตั้งใหม่ 5 จังหวัดขาดข้อมูลช่วงแรก 696 จังหวัด-เดือน, การเปลี่ยนนิยามคอลัมน์ปี 2021–2022), และการแบ่งข้อมูลตามเวลาอย่างเคร่งครัด (`Train 1994–2015: 19,632 แถว`, `Val 2016–2017: 1,848 แถว`, `Test 2018–2022: 4,620 แถว`)
  - **Box R3 — ข้อค้นพบจากการสำรวจข้อมูล (EDA Findings):**
    - อ้างอิงภาพ `results/figures/eda_seasonality.png`, `eda_lag_correlation.png`, `eda_province_heterogeneity.png`, `eda_annual_trend_covid.png` พร้อมสรุปตัวเลขสำคัญ: อุณหภูมิสูงสุดเดือนเมษายน (`28.60°C`) นำหน้าจำนวนผู้ป่วยสูงสุดเดือนกรกฎาคม (`114.31` ราย/จังหวัด) อยู่ 2–3 เดือน ($r = 0.3940$), ฝนเริ่มตกหนักเดือนพฤษภาคม (`189.84 mm`) นำหน้า 0–1 เดือน ($r = 0.2853$), ความเหลื่อมล้ำระหว่างจังหวัดต่างกันถึง `49.78 เท่า` (กรุงเทพฯ `354.45` vs หนองบัวลำภู `7.12` ราย/เดือน ทำให้ถ้าใช้เกณฑ์เดียวทั้งประเทศจะมี `11 จังหวัด` ไม่เคยได้รับคำเตือนเลย), และยุคโควิด-19 ที่ยอดผู้ป่วยลดลงถึง `11.30 เท่า` (`87,866` รายในปี 2019 เหลือ `7,778` รายในปี 2021)
  - **Box R4 — การเปรียบเทียบโมเดลกับ Baseline (Model vs. Baseline):**
    - อ้างอิงภาพ `results/figures/r4_model_vs_baseline.png` และตารางเปรียบเทียบทั้ง 3 Baselines กับ 3 ML Models บนชุด Test (`2018–2022`, `392` เดือนที่ระบาดจริง): ชี้ให้เห็นว่า `HistGradientBoosting` (เกณฑ์ตัดสิน `0.49` จากการจูน $F_2$ บนชุด Validation) ทำ **Test Recall ได้ถึง `88.27%` (`346/392`)** เหนือกว่า `Persistence` (`62.24%`, `244/392`) ถึง **`+26.03` percentage points** (ลดการหลุดเตือนจาก `148` เหลือเพียง `46` ครั้ง หรือลดลง `68.9%`) และทนทานต่อยุคโควิด-19 (`Recall 89.22%` ในยุคปกติ และ `86.18%` ในยุคโควิด)
  - **Box R5 — การวิเคราะห์ความผิดพลาดของโมเดล (Know Where the Model Fails):**
    - อ้างอิงภาพ `results/figures/r5_error_analysis.png` พร้อมตารางแยกแยะ:
      1. **เดือนเริ่มระบาดใหม่ (Onset, 148 ครั้ง) vs ระบาดต่อเนื่อง (Ongoing, 244 ครั้ง):** `Persistence` จับเดือนเริ่มระบาดใหม่ได้ **`0.0%` (0/148)** ในขณะที่ `HistGradientBoosting` จับได้ล่วงหน้าถึง **`73.0%` (108/148)** ส่วน `46` ครั้งที่โมเดลหลุดเตือน (`FN`) เป็นการพุ่งขึ้นแบบฉับพลัน (`Onset`) ถึง **`87.0%` (40/46)** ที่ยอดผู้ป่วยกระโดดเฉลี่ย `3.35 เท่า` ในเดือนเดียว (เช่น บึงกาฬ พ.ค. 2019 กระโดด `14.1x` จาก 7 เป็น 99 ราย, สิงห์บุรี มิ.ย. 2019 กระโดด `10.5x`, อุดรธานี ก.ค. 2020 กระโดด `10.4x`)
      2. **กายวิภาคของ False Positives (`295` ครั้ง):** ถึง **`93.6%` (276/295)** เป็นสัญญาณเตือนที่มีคุณค่าทางสาธารณสุข ได้แก่ ยอดผู้ป่วยสูงกว่าค่าเฉลี่ยจ่อเกณฑ์ระบาด `41.0%` (121 ครั้ง เช่น สมุทรสาคร มิ.ย. 2018 มี 64.0 ราย ห่างเกณฑ์ 64.5 เพียง 0.5 ราย), ช่วงขาลงหลังเพิ่งระบาด `36.9%` (109 ครั้ง เช่น เลย ส.ค. 2019), และเตือนล่วงหน้าก่อนระบาดจริงในเดือน $t+2$ อีก `15.6%` (46 ครั้ง เช่น ชัยภูมิ พ.ค. 2019) มีเพียง **`6.4%` (19/295)** เท่านั้นที่เป็นการเตือนผิดพลาดแท้จริง
  - **Box R6 — ข้อเสนอแนะเชิงปฏิบัติการและการวิเคราะห์ความคุ้มค่า (Practical Recommendation & Limits):**
    - อ้างอิงภาพ `results/figures/r6_threshold_policy.png` และเสนอ **ระบบเตือนภัย 2 ระดับ (Two-Tier Early Warning Protocol)** สำหรับ สสจ.:
      - **สีเขียว ($p < 0.35$, 83.8% ของเดือนทั้งหมด):** ความเสี่ยงระบาดต่ำเพียง `0.90%` -> เฝ้าระวังตามปกติผ่าน รง.506
      - **สีเหลือง Tier-1 Watch ($0.35 \le p < 0.65$, 4.8% ของเดือน):** ความเสี่ยง `17.12%` (0.58 ครั้ง/จังหวัด/ปี) -> ใช้มาตรการต้นทุนต่ำ (`0.3x`) ให้ อสม. รณรงค์คว่ำภาชนะกำจัดลูกน้ำยุงลายและตรวจสต็อกทรายอะเบท
      - **สีแดง Tier-2 High Alert ($p \ge 0.65$, 11.4% ของเดือน):** ความเสี่ยงสูงถึง `60.53%` (1.37 ครั้ง/จังหวัด/ปี) -> เปิดศูนย์ EOC พ่นหมอกควัน/ULV จุดเสี่ยง และเตรียมเตียง/สารน้ำ Ringer's lactate ล่วงหน้า 1 เดือน
      - รวมเตือนภัย (`p >= 0.35`) จับการระบาดได้ถึง **`91.07%` (357/392 ครั้ง)** และประหยัดต้นทุนรวม (`Total Normalized Cost`) เหนือกว่าทุกวิธีเมื่อ $R \ge 3$ (ประหยัดต้นทุน `65.9%–69.7%` เทียบกับการรณรงค์ปูพรมหน้าฝน 6 เดือน และลดงานแจ้งเตือนลง `72.2%` / ลดการเตือนเก้อลง `85.0%` ที่เกณฑ์เดี่ยว `0.49`) พร้อมปรับลดการเตือนอัตโนมัติ `56.0%` ในช่วงโควิด-19
      - **ข้อจำกัดที่ข้อมูลพิสูจน์ไม่ได้ 4 ข้อ:** (1) ข้อมูลเฝ้าระวังบอกความเสี่ยงแต่ไม่ได้พิสูจน์ผลเชิงสาเหตุว่ามาตรการลดผู้ป่วยได้กี่เปอร์เซ็นต์, (2) ความละเอียดระดับจังหวัด (`Admin1`) ต้องใช้ร่วมกับข้อมูลระดับตำบล/หมู่บ้านเพราะยุงลายบินได้ไกล 100–400 เมตร, (3) ไม่มีข้อมูลการเปลี่ยนสายพันธุ์ไวรัส (DENV-1..4) และภูมิคุ้มกันหมู่, (4) สภาพอากาศจากจุดศูนย์กลางจังหวัดไม่อาจแทนพฤติกรรมการเก็บน้ำในครัวเรือนได้ทั้งหมด
  - **Box R7 — บันทึกการใช้ AI และการตรวจสอบแก้ไข (AI-Use Log):**
    - ตารางสรุปกรณีจริงที่ทีมตรวจสอบพบข้อผิดพลาดของ AI และสั่งแก้ไข (เช่น การอ้างอิงวิธีคำนวณจุดศูนย์กลางจังหวัดด้วย LAEA/shapely ที่ไม่มีในโค้ดจริงใน T02, การแก้ปัญหา `HistGradientBoostingClassifier` ไม่มี `.feature_importances_` โดยเปลี่ยนเป็น Validation Permutation Importance ใน T07, การตรวจสอบและแก้ไขป้ายข้อความทับกราฟใน R3/R4/R5/R6, และการล็อกกฎป้องกัน Data Leakage)

## Out of scope
- Do not modify any upstream data or model outputs.

## Acceptance criteria (run these, paste real output in the handoff)
1. `python src/poster/build_poster_content.py` → exits with code `0` and generates `poster/poster_R1_to_R7_th.md` and `_agent/docs/SUMMARY_TH.md`.
2. `pytest` → all tests (including `tests/test_poster_numbers.py`) pass with 0 errors.

## Known pitfalls
- Always read and write markdown files with `encoding="utf-8"` on Windows so Thai characters render cleanly without `cp874`/`cp1252` encoding errors.
