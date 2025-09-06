# HeartLytics: Secure Role‑Based Heart Disease Prediction Web Application

**Authors:** HMRS Samaranayaka

**Affiliation:** NSBM Green University, Homagama, Sri Lanka

**Date:** 2025-09-06

## Abstract
HeartLytics is a full-stack Flask application that predicts the risk of heart disease and couples machine learning with rigorous security and usability controls. A Random Forest model trained on the UCI Heart Disease dataset powers single and batch predictions, while Exploratory Data Analysis (EDA) and outlier detection aid interpretability. Role-based access control, application-level envelope encryption, Argon2id password hashing, and CSRF protection safeguard patient data. A persistent light/dark theme, responsive charts, and PDF reporting deliver a cohesive user experience. This thesis documents the system's architecture, data flows, security model, theming, and comprehensive test strategy that collectively demonstrate HeartLytics as a secure clinical decision-support prototype.

## Table of Contents
- [List of Figures](#list-of-figures)
- [List of Tables](#list-of-tables)
- [Repository Snapshot](#repository-snapshot)
- [1. Working Topic](#1-working-topic)
- [2. Study Area & Study Objectives](#2-study-area--study-objectives)
- [3. Research Gap](#3-research-gap)
- [4. Research Problem / Questions](#4-research-problem--questions)
- [5. Research Strategy & Method](#5-research-strategy--method)
- [6. System Overview & Architecture](#6-system-overview--architecture)
  - [6.1 Context Diagram](#61-context-diagram)
  - [6.2 High-Level Architecture Diagram](#62-high-level-architecture-diagram)
  - [6.3 Deployment View](#63-deployment-view)
- [7. Data Flow Diagrams](#7-data-flow-diagrams)
  - [7.1 Level-0 DFD](#71-level-0-dfd)
  - [7.2 Level-1 DFD – Predict Workflow](#72-level-1-dfd--predict-workflow)
  - [7.3 Level-1 DFD – Batch Pipeline](#73-level-1-dfd--batch-pipeline)
- [8. Data Model & ERD](#8-data-model--erd)
- [9. Security Architecture](#9-security-architecture)
- [10. UI/UX & Theming](#10-uiux--theming)
- [11. Key Execution Flows](#11-key-execution-flows)
- [12. Implementation & Configuration](#12-implementation--configuration)
- [13. Testing & Evaluation](#13-testing--evaluation)
- [14. Timeline & Project Management](#14-timeline--project-management)
- [15. Ethics, Privacy & Compliance](#15-ethics-privacy--compliance)
- [16. Results, Discussion & Conclusion](#16-results-discussion--conclusion)
- [17. References](#17-references)
- [Appendix A — Full Test Cases](#appendix-a--full-test-cases)
- [Appendix B — API Endpoint Catalog](#appendix-b--api-endpoint-catalog)
- [Appendix C — RBAC Matrix & Permission Mapping](#appendix-c--rbac-matrix--permission-mapping)
- [Appendix D — Extended Figures](#appendix-d--extended-figures)
- [Appendix E — Glossary & Acronyms](#appendix-e--glossary--acronyms)

## List of Figures
No figures are included in this initial pass. Subsequent passes will enumerate and link all diagrams.

## List of Tables
No tables are included in this initial pass. Subsequent passes will enumerate and link all tabular content.

## Repository Snapshot
- **Commit Hash:** dcc7a3623f37a4b69d4b0f97a041af07ac757147
- **Commit Date:** 2025-09-06 13:30:20 +0530

### Stack Inventory
HeartLytics is implemented in Python 3 using the Flask web framework and Jinja2 templates. Persistent data is managed via SQLAlchemy ORM over SQLite by default, with environment-driven database configuration. Machine learning features rely on scikit-learn, pandas, numpy, and a pre-trained Random Forest model. Front-end styling leverages Bootstrap 5, custom CSS, and Plotly.js for interactive charts. ReportLab generates PDF summaries.

### Module Inventory
Key modules include:
- **auth/** – authentication forms, role-based decorators, and RBAC policy definitions.
- **routes/** – blueprints for prediction, settings, debugging utilities, and module access checks.
- **services/** – domain logic for data cleaning, simulation, PDF generation, security utilities, theming hooks, and cryptographic helpers (AEAD, envelope encryption, keyring management).
- **doctor/**, **user/**, **superadmin/** – role-specific dashboards and management interfaces.
- **templates/** – Jinja templates for pages and components.
- **static/** – stylesheets, scripts, and assets including chart theming scripts.
- **tests/** – pytest suites covering authentication, encryption, RBAC, dashboards, simulations, uploads, and theming.

### Data Model Inventory
The database schema (see [database.md](database.md)) defines tables `user`, `role`, `user_roles`, `patient`, `prediction`, `cluster_summary`, and `audit_log`. Encrypted fields appear in `patient` and `prediction` as groups of columns (`*_ct`, `_nonce`, `_tag`, `_wrapped_dk`, `_kid`, `_kver`). Foreign keys connect predictions to clustering summaries and users to roles and audit entries.

### Security Inventory
Security controls span authentication via Flask-Login, Argon2id password hashing with legacy PBKDF2 upgrade, CSRF decorators for forms and APIs, rate limiting on login attempts, security headers, and strict role-based access control enforced by decorators. Application-level envelope encryption uses AES-256-GCM with per-record data keys wrapped by a pluggable keyring; rollout flags (`ENCRYPTION_ENABLED`, `READ_LEGACY_PLAINTEXT`, `KMS_PROVIDER`, `KMS_KEY_ID`) govern operation. TLS is expected in production deployments.

### Theming Inventory
Light mode is the default. A `theme` cookie and `localStorage` entry persist the preference, read server-side on every request to avoid flashes of incorrect styling. `static/theme.charts.js` patches Plotly and Chart.js so visualizations adapt automatically. Dark mode renders charts with transparent backgrounds and adjusted text colors. The theme toggle appears on login and signup pages and all authenticated views.

### Testing Inventory
Automated tests reside under `tests/` and include suites for authentication (`test_auth.py`), password policies (`test_passwords.py`), encryption utilities (`test_crypto.py`, `test_encrypted_fields.py`), RBAC (`test_rbac.py`), theming (`test_theme.py`), dashboard and upload workflows, simulations, superadmin operations, and EDA payload handling. `TEST_CASES.md` enumerates manual and automated scenarios across modules, prioritizing security and functionality.

### Timeline Inventory
`gantt_chart.md` provides a mermaid Gantt diagram detailing phases: Planning (requirements, feasibility), Development (backend, frontend, model, security, RBAC, theming), Testing (unit/integration, user acceptance), Deployment, and Post-Deployment monitoring. Recent iterations added cleaning-log normalization, batch prediction notices, and theme toggle improvements on authentication pages.

## 1. Working Topic
HeartLytics delivers clinician-friendly heart disease risk prediction through a Flask-based web application secured by role-based access control and envelope encryption. Stakeholders include doctors, administrators, and end-users seeking interpretable predictions. The system's value lies in combining accurate machine learning with robust security and accessible theming.


## 2. Study Area & Study Objectives
Cardiovascular diseases account for nearly one third of global deaths, with lifestyle factors and limited access to early diagnostics exacerbating risks in low-resource settings. Digital decision-support systems can widen access to preventive care by transforming raw clinical measurements into actionable insights. HeartLytics positions itself in this domain as a web platform that integrates machine learning, exploratory analytics, and secure data management tailored for clinicians and researchers.

The primary functional objectives are:
1. **Accurate Prediction:** Use a tuned Random Forest model (`ml/model.pkl`) to classify patient records with probability estimates.
2. **Batch Processing and EDA:** Allow CSV uploads, automatic cleaning, outlier detection via IQR, Isolation Forest, Z-Score, LOF, and DBSCAN, and a dashboard summarizing distributions and correlations.
3. **Role-Specific Dashboards:** Provide dedicated views for Users, Doctors, Administrators, and SuperAdmins with module restrictions enforced through decorators.
4. **Reporting:** Generate per-patient and aggregate PDF reports using ReportLab, embedding charts and tables that respect the active theme.

Non-functional objectives emphasize:
- **Security:** Envelope encryption for patient identifiers and data, Argon2id password hashing, CSRF protection, and audit logging.
- **Usability:** Responsive Bootstrap 5 interface, persistent theming, accessible color contrast, and informative error feedback.
- **Maintainability:** Modular blueprints, service-oriented helpers for data and encryption, and comprehensive automated tests.

Collectively, these objectives align with stakeholders' needs for trustworthy, interpretable, and secure heart disease risk assessment.

## 3. Research Gap
Prior research often focuses on improving algorithmic performance of heart disease prediction but overlooks operational security and role differentiation. The bundled research paper emphasizes theming and user experience improvements but offers limited discussion on encryption or RBAC enforcement. Moreover, while studies highlight accuracy of machine learning models on the UCI dataset, few describe full-stack implementations that handle sensitive data with envelope encryption or provide audit-ready role separation. HeartLytics fills this gap by coupling predictive modeling with production-grade security practices and a theming system that adapts charts and tables for readability across light and dark modes.

## 4. Research Problem / Questions
The overarching problem is delivering machine learning predictions for heart disease in a way that remains secure, auditable, and user-friendly. The project investigates:
1. How can application-level envelope encryption be implemented without degrading user experience or system performance?
2. What RBAC policies balance clinician autonomy with administrative oversight and minimal attack surface?
3. In what ways does theme persistence influence comprehension of charts and logs across devices and sessions?
4. Can comprehensive EDA and outlier detection improve trust in model predictions for clinical decision-making?
5. How do automated tests and logs support verification of security controls and functional workflows?

## 5. Research Strategy & Method
HeartLytics follows Design Science Research Methodology (DSRM) by iteratively designing, building, and evaluating artefacts—namely the Flask application, encryption utilities, and theming modules. Requirements were elicited from documentation of clinical datasets and security best practices. Development cycles produced incremental prototypes tested via pytest and manual scenarios in `TEST_CASES.md`. Data originates from the UCI Heart Disease repository, preprocessed into model features using pandas and scikit-learn. Evaluation combines quantitative metrics (prediction probabilities, test outcomes, log entries) with qualitative assessment of usability. The methodology aligns with Peffers et al. (2007), ensuring that constructed artefacts address identified gaps and provide a foundation for further academic and clinical validation.

