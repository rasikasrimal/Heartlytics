# HeartLytics: Comprehensive System Thesis

## Title Page {#title-page}

**Project Title:** HeartLytics – Heart Disease Risk Prediction Web Application  \
**Authors:** HMRS Samaranayaka, Rasika Srimal, and Contributors  \
**Affiliation:** Department of Computer Science & Software Engineering, NSBM Green University  \
**Date:** 2025-09-06  \

## Abstract {#abstract}
HeartLytics is a full-stack Flask application that predicts heart disease risk using a tuned Random Forest model trained on the UCI Heart Disease dataset. The system enables individual patient assessment and batch analysis via CSV uploads, delivering interactive dashboards and PDF reports. Role-based access control separates regular users, doctors, administrators, and super administrators, while CSRF protection, security headers, and rate limiting strengthen resilience. The project integrates data cleaning, exploratory data analysis, simulation modules, and exportable research content. This thesis documents the design, implementation, and evaluation of HeartLytics, detailing its architecture, data flow, security posture, user interface theming, and testing strategy. It serves as both a technical exposition and a reference for extending the platform toward clinical-grade decision support.

## Table of Contents {#table-of-contents}
1. [Working Topic](#1-working-topic)
2. [Study Area & Study Objectives](#2-study-area-and-study-objectives)
3. [Research Gap](#3-research-gap)
4. [Research Problem / Questions](#4-research-problem--questions)
5. [Research Strategy & Method](#5-research-strategy--method)
6. [System Overview & Architecture](#6-system-overview--architecture)
7. [Data Flow Diagrams](#7-data-flow-diagrams)
8. [Data Model & ERD](#8-data-model--erd)
9. [Security Architecture](#9-security-architecture)
10. [UI/UX & Theming](#10-uiux--theming)
11. [Key Execution Flows](#11-key-execution-flows)
12. [Implementation & Configuration](#12-implementation--configuration)
13. [Testing & Evaluation](#13-testing--evaluation)
14. [Timeline & Project Management](#14-timeline--project-management)
15. [Ethics, Privacy & Compliance](#15-ethics-privacy--compliance)
16. [Results, Discussion & Conclusion](#16-results-discussion--conclusion)
17. [References](#17-references)

### Appendices
A. [Full Test Cases](#appendix-a--full-test-cases)  
B. [API Endpoint Catalog](#appendix-b--api-endpoint-catalog)  
C. [RBAC Matrix & Permission Mapping](#appendix-c--rbac-matrix--permission-mapping)  
D. [Extended Figures](#appendix-d--extended-figures)  
E. [Glossary & Acronyms](#appendix-e--glossary--acronyms)

## List of Figures {#list-of-figures}
*(To be populated in later passes.)*

## List of Tables {#list-of-tables}
*(To be populated in later passes.)*

## Repository Snapshot {#repository-snapshot}
- **Commit Hash:** b6b60ae12d8944467a976d031e53b60afad2996a
- **Commit Date:** 2025-09-06 13:06:38 +0530
- **Tech Stack:** Python, Flask, Flask-SQLAlchemy, scikit-learn, pandas, numpy, Jinja2, Bootstrap 5, Plotly.js, ReportLab
- **Key Modules:** `auth`, `routes` (`predict`, `settings`), `services` (`auth.py`, `data.py`, `pdf.py`, `security.py`, `simulation.py`), blueprints for `doctor`, `user`, and `superadmin`
- **Data Model:** SQLite database with tables `audit_log`, `cluster_summary`, `patient`, `prediction`, `role`, `user`, and `user_roles`
- **Security Features:** Flask-Login authentication, role-based authorization, password hashing via Werkzeug, CSRF tokens, security headers, and guidance for TLS and encrypted storage
- **Theming:** Responsive Bootstrap 5 interface with sticky footer, redesigned login page, chart theming, and dark/light modes
- **Testing Artifacts:** Pytest suites including `test_predict.py`, `test_auth.py`, `test_dashboard.py`, `test_eda_payload.py`, `test_simulations.py`, `test_superadmin_dashboard.py`, and `test_upload.py`
- **Timeline Reference:** Development phases documented in `gantt_chart.md` covering planning, development, testing, deployment, and post-deployment periods

---

## 1. Working Topic {#1-working-topic}
HeartLytics investigates how a web-based, role-aware platform can deliver individualized and batch heart disease predictions using machine learning. Stakeholders include patients, doctors, administrators, and system maintainers. The system provides clinical-style insights, auditability, and secure data management to support informed decision making.

## 2. Study Area & Study Objectives {#2-study-area-and-study-objectives}
Cardiovascular disease remains a pervasive global health challenge, accounting for millions of deaths annually. Early identification of at-risk individuals enables timely interventions, reducing morbidity and mortality. Traditional screening relies on clinical tests such as electrocardiograms or angiography, which, while accurate, can be resource intensive and invasive. HeartLytics situates itself within this domain by leveraging routinely collected clinical attributes—age, sex, chest pain type, blood pressure, cholesterol levels, fasting blood sugar, electrocardiographic results, heart rate, exercise-induced angina, ST depression, slope of peak exercise ST segment, number of major vessels, and thalassemia type—to deliver predictive insights.

The study is motivated by the need for accessible, explainable, and scalable tools that integrate seamlessly into existing healthcare workflows. Many existing solutions focus either on model accuracy without deployment considerations or on simplistic calculators lacking data governance. HeartLytics bridges this gap by combining a tuned Random Forest model with a fully featured web application. The platform supports:

- **Individual Predictions:** Users enter patient data via a validated form. The system returns a binary prediction, probability, risk band, and confidence score, mapping directly to clinical decision support.
- **Batch Analysis:** Healthcare providers can upload CSV files to run multiple predictions. The application performs data cleaning, generates exploratory data analysis (EDA) artifacts, and logs outliers through algorithms such as Isolation Forest and Local Outlier Factor.
- **Interactive Dashboard:** Visualizations include risk distributions, box plots, correlation heatmaps, and cluster analyses summarizing patient segments. Results can be exported to PDF, enabling offline review and sharing.
- **Role-Based Interfaces:** Separate dashboards exist for doctors, regular users, and administrators. A SuperAdmin panel manages user approvals, role changes, and audit logs, ensuring accountability and regulatory compliance.
- **Research Content Integration:** The application bundles a LaTeX-based research manuscript, rendered with MathJax and media assets, allowing users to contextualize the model's development and validation.

Non-functional objectives are equally significant. Security measures such as CSRF tokens, security headers, and session management defend against common web threats. Usability considerations include a modern Bootstrap 5 theme, sticky footer, and responsive layouts. The theming system supports light and dark modes, ensuring accessibility and visual consistency. Performance goals are addressed through efficient model inference and streamlined data pipelines, while maintainability is aided by modular blueprints and service layers. Together, these objectives anchor HeartLytics as a comprehensive, production-ready prototype for heart disease risk prediction.

## 3. Research Gap {#3-research-gap}
The accompanying research paper compares Random Forest and XGBoost models on the UCI dataset, highlighting strong predictive performance but acknowledging limitations such as modest dataset size and gender imbalance. Existing literature often emphasizes algorithmic accuracy without integrating full-stack deployment, robust security, or user-role differentiation. HeartLytics addresses these gaps by: (1) embedding security best practices—password hashing, CSRF protection, and role-based access control—directly into the application; (2) providing a workflow that spans single predictions, batch processing, EDA, and PDF reporting; and (3) incorporating user experience elements like theming and responsive design. By coupling model insights with operational features and governance, HeartLytics moves beyond standalone model evaluations toward a holistic, deployable solution.

## 4. Research Problem / Questions {#4-research-problem--questions}
The core problem is how to deliver reliable heart disease risk predictions through a secure, user-friendly web platform that accommodates diverse roles and data workflows. This leads to the following research questions:

1. **How can machine learning models be integrated into a Flask application to provide accurate and interpretable heart disease predictions for both individual and batch inputs?**
2. **What architectural and security patterns ensure that sensitive health data remains protected while supporting role-based access and audit trails?**
3. **In what ways do theming and interface design choices influence usability and adoption among medical professionals and patients?**
4. **How effective is the system at generating actionable analytics—such as outlier detection and clustering—that support clinical decision making?**

## 5. Research Strategy & Method {#5-research-strategy--method}
HeartLytics follows a design science research approach, iteratively constructing and evaluating an artifact that addresses a real-world problem. The methodology aligns with the Design Science Research Methodology (DSRM) articulated by Peffers et al. (2007), encompassing problem identification, objective definition, design and development, demonstration, evaluation, and communication.

Data collection centers on the UCI Heart Disease dataset, augmented during runtime by user-submitted records and batch uploads. The system captures logs and audit trails, enabling subsequent analysis of usage patterns and security events. Quantitative metrics—such as model accuracy, prediction latency, and dashboard response times—are gathered through automated tests and monitoring hooks. Qualitative feedback may be obtained from user studies or expert reviews during deployment phases.

Analysis involves preprocessing pipelines for missing values and outlier detection, followed by model inference using a tuned Random Forest classifier. Statistical summaries and visualizations aid interpretation. Security analysis assesses compliance with best practices for authentication, authorization, and data protection. Findings guide iterative refinements, demonstrating the artifact's utility and informing future enhancements.

