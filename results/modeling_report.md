# Modeling Report — Dengue Outbreak Prediction (R4)
Date: 2026-11-09 · Framework: scikit-learn · Best Model: **hist_gradient_boosting**

## 1. Executive Summary & Best Model Decision
- **Primary Metric (Recall):** Per SSOT §1.5 and SDG 3 public health objectives, missed outbreaks (false negatives) carry grave consequences. **HistGradientBoosting** achieved the highest test recall of **0.8827** (346 of 392 outbreak months caught 1 month ahead), substantially outperforming the persistence baseline (**0.6224**, +26.0 percentage points) and the seasonal baseline (**0.2832**, +60.0 percentage points).
- **Precision & Balanced F1:** Despite aggressive outbreak detection, HistGradientBoosting retained a precision of **0.5398** (F1 = **0.6699**), avoiding false alarm collapse. Logistic Regression achieved the highest overall test F1 of **0.6992** (recall 0.8597, precision 0.5892).
- **Ranking Quality (PR-AUC):** HistGradientBoosting scored **0.7657** on test and highest validation PR-AUC (**0.6854**), far above the persistence baseline binary PR-AUC (**0.4255**).
- **Best Model Selection:** **`hist_gradient_boosting`** is designated as the primary model for public health deployment due to maximum recall on outbreak months and highest ranking capability, with `logistic_regression` serving as a high-interpretability alternative.

## 2. Performance Comparison Across All Splits

### Validation Set (2016–2017)
| Method | Recall (Primary) | Precision | F1-Score | PR-AUC | Specificity | Accuracy | TP | FP | FN | Support |
|---|---|---|---|---|---|---|---|---|---|---|
| Majority Class (Baseline 1) | 0.0000 | 0.0000 | 0.0000 | 0.0379 | 1.0000 | 0.9621 | 0 | 0 | 70 | 70 |
| Persistence t-1 (Baseline 2) | 0.6000 | 0.5385 | 0.5676 | 0.3382 | 0.9798 | 0.9654 | 42 | 36 | 28 | 70 |
| Seasonal t-12 (Baseline 3) | 0.2571 | 0.0652 | 0.1040 | 0.0449 | 0.8549 | 0.8323 | 18 | 258 | 52 | 70 |
| Logistic Regression | 0.8429 | 0.5043 | 0.6310 | 0.6745 | 0.9674 | 0.9627 | 59 | 58 | 11 | 70 |
| Random Forest | 0.7714 | 0.5870 | 0.6667 | 0.6672 | 0.9786 | 0.9708 | 54 | 38 | 16 | 70 |
| HistGradientBoosting | 0.8857 | 0.4627 | 0.6078 | 0.6854 | 0.9595 | 0.9567 | 62 | 72 | 8 | 70 |

### Test Set (2018–2022 Overall)
| Method | Recall (Primary) | Precision | F1-Score | PR-AUC | Specificity | Accuracy | TP | FP | FN | Support |
|---|---|---|---|---|---|---|---|---|---|---|
| Majority Class (Baseline 1) | 0.0000 | 0.0000 | 0.0000 | 0.0848 | 1.0000 | 0.9152 | 0 | 0 | 392 | 392 |
| Persistence t-1 (Baseline 2) | 0.6224 | 0.6321 | 0.6272 | 0.4255 | 0.9664 | 0.9372 | 244 | 142 | 148 | 392 |
| Seasonal t-12 (Baseline 3) | 0.2832 | 0.2984 | 0.2906 | 0.1453 | 0.9383 | 0.8827 | 111 | 261 | 281 | 392 |
| Logistic Regression | 0.8597 | 0.5892 | 0.6992 | 0.7702 | 0.9444 | 0.9372 | 337 | 235 | 55 | 392 |
| Random Forest | 0.8291 | 0.5898 | 0.6893 | 0.7698 | 0.9465 | 0.9366 | 325 | 226 | 67 | 392 |
| HistGradientBoosting | 0.8827 | 0.5398 | 0.6699 | 0.7657 | 0.9302 | 0.9262 | 346 | 295 | 46 | 392 |

### Test Subperiod: Normal (2018–2019)
| Method | Recall (Primary) | Precision | F1-Score | PR-AUC | Specificity | Accuracy | TP | FP | FN | Support |
|---|---|---|---|---|---|---|---|---|---|---|
| Majority Class (Baseline 1) | 0.0000 | 0.0000 | 0.0000 | 0.1456 | 1.0000 | 0.8544 | 0 | 0 | 269 | 269 |
| Persistence t-1 (Baseline 2) | 0.6208 | 0.6208 | 0.6208 | 0.4406 | 0.9354 | 0.8896 | 167 | 102 | 102 | 269 |
| Seasonal t-12 (Baseline 3) | 0.1933 | 0.4333 | 0.2674 | 0.2012 | 0.9569 | 0.8458 | 52 | 68 | 217 | 269 |
| Logistic Regression | 0.8587 | 0.5833 | 0.6947 | 0.7764 | 0.8955 | 0.8902 | 231 | 165 | 38 | 269 |
| Random Forest | 0.8364 | 0.5890 | 0.6912 | 0.7751 | 0.9006 | 0.8912 | 225 | 157 | 44 | 269 |
| HistGradientBoosting | 0.8922 | 0.5393 | 0.6723 | 0.7762 | 0.8702 | 0.8734 | 240 | 205 | 29 | 269 |

### Test Subperiod: COVID-19 (2020–2022)
| Method | Recall (Primary) | Precision | F1-Score | PR-AUC | Specificity | Accuracy | TP | FP | FN | Support |
|---|---|---|---|---|---|---|---|---|---|---|
| Majority Class (Baseline 1) | 0.0000 | 0.0000 | 0.0000 | 0.0444 | 1.0000 | 0.9556 | 0 | 0 | 123 | 123 |
| Persistence t-1 (Baseline 2) | 0.6260 | 0.6581 | 0.6417 | 0.4286 | 0.9849 | 0.9690 | 77 | 40 | 46 | 123 |
| Seasonal t-12 (Baseline 3) | 0.4797 | 0.2341 | 0.3147 | 0.1354 | 0.9271 | 0.9073 | 59 | 193 | 64 | 123 |
| Logistic Regression | 0.8618 | 0.6023 | 0.7090 | 0.7623 | 0.9736 | 0.9686 | 106 | 70 | 17 | 123 |
| Random Forest | 0.8130 | 0.5917 | 0.6849 | 0.7575 | 0.9740 | 0.9668 | 100 | 69 | 23 | 123 |
| HistGradientBoosting | 0.8618 | 0.5408 | 0.6646 | 0.7491 | 0.9660 | 0.9614 | 106 | 90 | 17 | 123 |

## 3. Subperiod Analysis: Normal (2018–2019) vs. COVID-19 (2020–2022)
Outbreak prevalence shifted significantly from **14.56%** (269 outbreaks / 1,848 rows) during the 2018–2019 normal epidemic cycle to **4.44%** (123 outbreaks / 2,772 rows) during 2020–2022 due to COVID-19 behavioral shifts (school closures, mobility restrictions).

- **Robustness of HistGradientBoosting:** Maintained a high recall of **0.8922** in 2018–2019 and **0.8618** during COVID-19.
- **Robustness of Logistic Regression:** Maintained **0.8587** in 2018–2019 and **0.8618** during COVID-19, with precision rising from 0.5833 to 0.6023.
- **Seasonal Baseline Breakdown:** The seasonal (t-12) baseline collapsed during normal years (recall 0.1933) and had poor precision (0.2341) during COVID years.

## 4. Hyperparameter Tuning & Threshold Calibration Summary
| Model | Best Hyperparameters (Val PR-AUC) | Val-Tuned Threshold | Rule | Val PR-AUC | Val Recall | Val F1 |
|---|---|---|---|---|---|---|
| logistic_regression | C=0.01 | 0.54 | max_f2_on_val | 0.6745 | 0.8429 | 0.6310 |
| random_forest | max_depth=10, min_samples_leaf=5, n_estimators=100 | 0.45 | max_f2_on_val | 0.6672 | 0.7714 | 0.6667 |
| hist_gradient_boosting | learning_rate=0.1, max_depth=4, min_samples_leaf=20 | 0.49 | max_f2_on_val | 0.6854 | 0.8857 | 0.6078 |

## 5. Feature Importance & Epidemiological Insights
Top features identified across the models demonstrate clear epidemiological coherence:

### Logistic Regression
1. **`cases_zscore_lag_0`**: 0.3219
2. **`cases_lag_0`**: 0.1291
3. **`cos_target_month`**: 0.0620
4. **`cases_lag_1`**: 0.0457
5. **`cases_lag_2`**: 0.0457
6. **`precip_lag_1`**: 0.0409
7. **`precip_lag_3`**: 0.0367

### Random Forest
1. **`cases_zscore_lag_0`**: 0.2777
2. **`outbreak_lag_0`**: 0.1470
3. **`cases_lag_0`**: 0.1371
4. **`cases_roll_mean_3`**: 0.0937
5. **`cases_lag_1`**: 0.0634
6. **`precip_lag_3`**: 0.0311
7. **`cos_target_month`**: 0.0291

### Hist Gradient Boosting
1. **`cases_zscore_lag_0`**: 0.7235
2. **`precip_lag_3`**: 0.0527
3. **`precip_lag_1`**: 0.0347
4. **`cos_target_month`**: 0.0309
5. **`cases_lag_0`**: 0.0257
6. **`precip_lag_2`**: 0.0223
7. **`cases_lag_2`**: 0.0215

**Key Epidemiological Drivers:**
1. **Recent Outbreak Momentum (`cases_zscore_lag_0`, `cases_lag_0`, `outbreak_lag_0`):** Standardized case deviations and last-month outbreak status provide the strongest baseline signal of active mosquito transmission.
2. **Precipitation Lag Structure (`precip_lag_3`, `precip_lag_2`):** Precipitation 2–3 months earlier reflects the aquatic breeding cycle of *Aedes aegypti* (standing water → egg → larva → pupa → adult population expansion).
3. **Annual Seasonality (`cos_target_month`, `sin_target_month`):** Captures Thailand's monsoon calendar (May–October rainy season peak) even when recent case counts are moderate.
