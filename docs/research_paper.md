# Prediction of Heart Disease Using Machine Learning Algorithms

**Author:** HMRS Samaranayaka  
Department of Computer Science & Software Engineering  
NSBM Green University, Homagama, Sri Lanka  
hmrssamaranayaka.students.nsbm.ac.lk

## Abstract
Heart disease remains a leading cause of mortality worldwide. This paper develops a machine-learning system to predict heart disease using the UCI Heart Disease dataset. We perform robust preprocessing (missing value imputation, outlier mitigation, feature scaling) and conduct an extensive exploratory data analysis (EDA) to understand demographic and clinical patterns. We train and optimize ensemble classifiers—Random Forest and XGBoost—via grid search, and evaluate with accuracy, precision, recall, F1-score, and ROC–AUC. XGBoost slightly outperforms Random Forest (~92% vs. 91% accuracy). We deploy the best model in a Flask web application to demonstrate real-time usability. Results validate ensemble methods for clinical decision support and highlight data characteristics that influence model performance.

## Keywords
Heart Disease, Machine Learning, Random Forest, XGBoost, Exploratory Data Analysis, Flask, Clinical Decision Support

## Introduction
Cardiovascular diseases (CVDs) are the leading cause of global mortality, with an estimated 17.9 million deaths annually [1]. Early detection of heart disease is crucial to reduce morbidity and mortality. While tests such as ECG and angiography remain gold standards, machine learning (ML) can complement clinical workflows by learning patterns from multi-attribute patient data.

Recent work shows strong performance for supervised ML models in heart disease prediction, particularly tree ensembles (Random Forest, Gradient Boosting) that capture nonlinearity and interactions [2, 3]. In this study, we:

1. Preprocess and analyze the UCI Heart Disease dataset.
2. Perform EDA to characterize demographics and risk-factor distributions.
3. Train and tune Random Forest and XGBoost models.
4. Compare models on accuracy, precision, recall, F1, and ROC–AUC.
5. Deploy the best model as a Flask web application.
6. Secure the password reset flow using Gmail SMTP with diagnostics, enforce re-authentication after reset, and offer optional TOTP-based 2FA with recovery codes.
7. Provide fallback email-based one-time codes as a lower-assurance MFA option.
8. Mask destination emails during verification to protect user privacy.
9. Redesign the forgot-password interface using Bootstrap 5 cards and segmented OTP inputs for improved accessibility.

## Dataset and Exploratory Data Analysis (EDA)

### Dataset Description
We use the UCI Heart Disease repository [4], consolidated across Cleveland (USA), Hungarian Institute of Cardiology, University Hospital Zurich (Switzerland), and V.A. Medical Center Long Beach (USA). After harmonization, the working table contains ~920 instances and 16 attributes. The raw target \(num \in \{0,1,2,3,4\}\) indicates disease severity; we binarize to \( \texttt{target\_bin} = \mathbf{1}(num > 0) \).

Outcome prevalence is approximately 55.3% positive vs. 44.7% negative. Core features include: *age*, *sex*, chest pain type (*cp*), resting blood pressure (*trestbps*), cholesterol (*chol*), maximum heart rate (*thalach*), ST depression (*oldpeak*), number of vessels (*ca*), and thalassemia status (*thal*).

### EDA Highlights and Figures
**Gender distribution.** The dataset is male-skewed (~79% male), raising fairness considerations (Fig. 1).

**Dataset×Gender.** A heatmap (Fig. 2) shows male predominance across centers with site-specific skews.

**Age by dataset.** Box plots (Fig. 3) reveal age shifts and outliers between centers, implying potential domain shift.

**Heart disease vs. chest pain type.** Stacked bars (Fig. 4) show *asymptomatic* has the highest positive rate (~79%), while *atypical angina* is lowest (~14%).

**Age by chest pain type.** Histogram with marginal boxplot (Fig. 5) shows older ages aligned with asymptomatic/typical angina.

**Resting blood pressure (BP).** Boxplots by disease status (Fig. 6) show higher central tendency in positives; stage-wise histograms with KDE (Fig. 7) show gradual right-shift with severity.

**Cholesterol by stage.** Violin plots (Fig. 8) show stage-wise differences in distribution and spread.

![Gender distribution (donut)](fig1_gender_donut.png)

![Dataset × Gender counts (heatmap)](fig2_dataset_gender_heatmap.png)

![Age distribution per dataset (box plot)](fig3_age_box_by_dataset.png)

![Heart disease frequency for each chest pain type (stacked bar)](fig4_cp_stacked_bar_target.png)

![Age distribution by chest pain type (histogram; marginal box)](fig5_age_hist_by_cp_with_marginal_box.png)

![Resting BP distribution by heart disease status (box plot)](fig6_trestbps_box_by_status.png)

![Resting BP distribution by disease stage (histogram with KDE)](fig7_trestbps_hist_kde_by_stage.png)

![Cholesterol distribution by disease stage (violin plots)](fig8_chol_violin_by_stage.png)

## Methodology

### Preprocessing
We detect and impute missing values (e.g., in *ca*, *thal*, *slope*) using iterative models (Random Forest classifier/regressor). Clinically implausible values (e.g., \(\textit{chol}=0\)) are treated as missing. Column-level outliers are flagged with the interpretable interquartile range (IQR) rule, and an Isolation Forest identifies patients with unusual feature patterns, providing an anomaly score. Numerical features are standardized (z-score). Categorical variables are retained as binary/ordinal or one-hot encoded as appropriate. Table 1 summarizes features.

| Feature  | Description |
|----------|-------------|
| Age      | Age in years |
| Sex      | 1 = male, 0 = female |
| CP       | Chest pain type (4 classes) |
| Trestbps | Resting blood pressure (mmHg) |
| Chol     | Serum cholesterol (mg/dL) |
| FBS      | Fasting blood sugar > 120 mg/dL (1/0) |
| Restecg  | Resting ECG result (0,1,2) |
| Thalach  | Maximum heart rate |
| Exang    | Exercise-induced angina (1/0) |
| Oldpeak  | ST depression (relative to rest) |
| Slope    | Slope of peak exercise ST (0,1,2) |
| CA       | Major vessels (0–3) |
| Thal     | Thalassemia (3, 6, 7) |
| Target   | 0 = No disease, 1 = Disease |

### Models and Tuning
We compare:

- **Random Forest (RF)** [5]: 100 trees, max depth 7, `class_weight=balanced`.
- **XGBoost** [3]: tuned via grid search, e.g., `n_estimators=150`, depth=3, learning rate=0.01, subsample=0.8, `colsample_bytree=0.8`.

Hyperparameters are optimized using 5-fold CV on the training set (stratified split, 70/30).

### Evaluation
We report accuracy, precision, recall, F1-score (positive class), ROC–AUC, and confusion matrices. In clinical screening, recall (sensitivity) is critical to minimize false negatives.

### Deployment
The best model is wrapped in a Flask web app [6]; inputs are preprocessed with the same pipeline and predictions (with confidence) are returned. A small dashboard summarizes recent usage statistics.

## Results and Discussion
Table 2 compares performance on the held-out test set (30%).

| Model         | Acc.  | Prec. | Rec. | F1  |
|---------------|-------|-------|------|-----|
| Random Forest | 91.2% | 0.93  | 0.91 | 0.92 |
| XGBoost       | 92.0% | 0.94  | 0.92 | 0.93 |

XGBoost slightly reduces both false positives and false negatives relative to RF. Feature importance (gain) highlights *cp*, *thal*, *ca*, and *oldpeak*, consistent with clinical intuition and prior work [2]. Overlap in *trestbps* and *chol* distributions (Figs. 6–8) underlines the value of ensembles that exploit multi-feature interactions.

**Deployment.** The Flask prototype returns instant predictions with confidence. Example stress tests confirm sensible risk dynamics (e.g., elevated BP/cholesterol with angina increases predicted risk).

**Limitations.** Dataset size is modest; gender/site skews warrant fairness analysis. External validation on independent cohorts is required for clinical adoption. Prototype deployment requires hardening (security, audit logs, governance).

## Conclusion and Future Work
We presented an end-to-end heart disease prediction system using the UCI dataset. EDA uncovered demographic and center-specific patterns; RF and XGBoost achieved strong results, with XGBoost best overall. A Flask app demonstrated practical deployment.

Future work includes: (i) larger, more diverse cohorts; (ii) threshold tuning for sensitivity-first screening; (iii) probability calibration; (iv) subgroup fairness audits; (v) external validation; and (vi) integration with clinical systems.

## References
1. World Health Organization, “Cardiovascular diseases (CVDs),” Fact Sheet, 2021. [Online]. Available: https://www.who.int/health-topics/cardiovascular-diseases  
2. D. Zhang et al., “Heart disease prediction based on the embedded feature selection method and deep neural network,” *Journal of Healthcare Engineering*, vol. 2021, Article ID 6260022, 2021. doi: 10.1155/2021/6260022.  
3. T. Chen and C. Guestrin, “XGBoost: A scalable tree boosting system,” in *Proc. 22nd ACM SIGKDD Int. Conf. Knowledge Discovery & Data Mining (KDD'16)*, San Francisco, CA, USA, 2016, pp. 785–794. doi: 10.1145/2939672.2939785.  
4. A. Janosi, W. Steinbrunn, M. Pfisterer, and R. Detrano, “Heart Disease Dataset,” UCI Machine Learning Repository, 1988. [Online]. Available: https://archive.ics.uci.edu/ml/datasets/Heart+Disease  
5. L. Breiman, “Random forests,” *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001. doi: 10.1023/A:1010933404324.  
6. A. Ronacher, “Flask Documentation,” Pallets Projects, v2.0, 2021. [Online]. Available: https://flask.palletsprojects.com

## Appendix: Hyperparameter Grids (Abbrev.)
**Random Forest:** `n_estimators ∈ {50,100,150}`, `max_depth ∈ {None,3,5,7,9}`, `min_samples_split ∈ {2,4,6,8}`, `min_samples_leaf ∈ {1,2,4}`, `class_weight=balanced`.

**XGBoost:** `n_estimators ∈ {100,150,200}`, `learning_rate ∈ {0.01,0.05,0.1}`, `max_depth ∈ {3,4,5}`, `subsample ∈ {0.6,0.8,1.0}`, `colsample_bytree ∈ {0.6,0.8,1.0}`, `γ ∈ {0,0.1,0.5}`.

© 2025 IEEE.

## Security Update
The web application now provides a secure forgotten password flow using short-lived verification codes hashed at rest to protect user accounts.

## Authentication Flow Enhancements
The web application now employs peppered hashes for password reset codes, enforced cooldowns on resend attempts, and a user-friendly countdown UI to reduce lockouts. These measures improve both security and usability in recovery scenarios.
