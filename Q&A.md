# Project Q&A

This document collects potential questions and answers about the Heartlytics project to help present a thorough understanding during a supervisor panel.

## 1. Project Overview

**Q1: What is the primary goal of the Heartlytics application?**
A1: It predicts the risk of heart disease for individual patients and batches using a trained Random Forest model while providing dashboards and PDF reports.

**Q2: Which dataset was used to train the model?**
A2: The model was trained on the UCI Heart Disease dataset, combining the Cleveland and other subsets.

**Q3: Which machine learning algorithm powers the predictions?**
A3: A scikit-learn Random Forest classifier tuned using GridSearchCV.

**Q4: What is the tech stack used in the backend?**
A4: Python with Flask, Flask-SQLAlchemy for the database layer, and additional libraries such as pandas, numpy, and scikit-learn for data processing and modeling.

**Q5: How is the project structured?**
A5: The repository has modules for authentication, services, routes/blueprints, templates, static assets, ML artifacts, and tests, centered around the main `app.py` entry point.

## 2. Data & Machine Learning

**Q6: Which features are collected for predictions?**
A6: Clinical features such as age, sex, chest pain type, blood pressure, cholesterol, fasting blood sugar, ECG results, max heart rate, exercise-induced angina, ST depression, slope, number of major vessels, and thalassemia type.

**Q7: How are batch predictions handled?**
A7: Users upload a CSV, map columns, undergo automatic cleaning, run outlier detection, and receive progress feedback before results appear in the dashboard.

**Q8: What kind of analysis is available in the dashboard?**
A8: KPIs like total predictions and positive rate, probability distributions, correlation heatmaps, box plots, and cluster analysis with scatter plots and profile tables.

**Q9: How does the app deal with missing values in `num_major_vessels`?**
A9: Batch prediction is resilient; if this column is missing, the process continues without failing.

**Q10: What outlier detection methods are supported?**
A10: IQR, Isolation Forest, Z-Score, Local Outlier Factor, and DBSCAN.

## 3. Application Architecture

**Q11: What role do Flask blueprints play in this project?**
A11: They modularize functionality into areas like prediction, settings, simulations, doctor views, user dashboards, and superadmin administration.

**Q12: How is the navigation bar tailored per role?**
A12: Navigation items are generated using RBAC helpers that check the current user's permissions, ensuring only allowed modules appear.

**Q13: Where are uploaded CSV files stored?**
A13: Uploaded files are saved under the instance folder within an `uploads` directory, which is ensured to exist at runtime.

**Q14: How are themes implemented?**
A14: A theme service initializes light and dark mode support; preferences are stored in localStorage and cookies, and chart libraries adapt automatically.

**Q15: What reporting capability is provided?**
A15: Users can export patient-level PDFs or a full dashboard report, with visuals and tables styled consistently.

## 4. Features & User Interaction

**Q16: What forms of prediction are available to users?**
A16: Single-form predictions for individual patients and batch predictions via CSV uploads.

**Q17: How does the application support simulations?**
A17: A simulations module offers what-if analysis where users tweak variables like age or exercise-induced angina to see risk projections.

**Q18: What interface elements enhance usability?**
A18: A responsive Bootstrap 5 UI, sticky footer and navigation, light/dark theme toggle, and motion utilities for subtle animations.

**Q19: How are cleaning logs presented?**
A19: Cleaning logs are normalized and theme-aware, stripping blank lines and showing concise notices in batch prediction results.

**Q20: What research materials does the app include?**
A20: A bundled LaTeX manuscript rendered with MathJax, including tables, figures, and reference links.

## 5. Security & Authentication

**Q21: What authentication features are implemented?**
A21: Standard login with optional TOTP-based 2-step verification, email-based MFA codes, six-digit password reset codes, and session timeouts.

**Q22: How does the app ensure data security?**
A22: It employs application-level envelope encryption for patient data and Argon2id password hashing.

**Q23: How are CSRF attacks mitigated?**
A23: CSRF tokens are applied to both form submissions and API requests, enforced through decorators.

**Q24: What role-based access control levels exist?**
A24: SuperAdmin, Admin, Doctor, and User roles with differing permissions over prediction, batch processing, dashboards, and research access.

**Q25: How are login attempts protected?**
A25: The application includes login rate limiting, session timeouts, and masked OTP delivery to protect against brute force attacks.

## 6. Deployment, Configuration & Testing

**Q26: Which configuration classes are used?**
A26: `DevelopmentConfig` for development and `ProductionConfig` for production, loaded based on the `FLASK_ENV` environment variable.

**Q27: Where is the trained model stored by default?**
A27: In the `ml/` directory as `model.pkl`, referenced by the `MODEL_PATH` environment variable.

**Q28: What environment variables are essential?**
A28: Variables for secret keys, database URI, model path, encryption settings, SMTP credentials, and OTP parameters as listed in `.env.example`.

**Q29: What is the default database used?**
A29: SQLite, managed via SQLAlchemy, with the default URI `sqlite:///instance/app.db`.

**Q30: How are tests executed?**
A30: Using `pytest`; the suite currently has over fifty tests covering prediction logic, RBAC, and MFA workflows.

