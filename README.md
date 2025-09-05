# Heartlytics

A full-stack **Flask** application for predicting the risk of heart disease using a trained **Random Forest** model (scikit-learn).
Users can enter patient data, upload CSV files for batch analysis, explore results in an interactive dashboard, and export rich PDF reports.

---

## ✨ Features
- 🧠 **ML Model**: Random Forest (GridSearchCV tuned), trained on the UCI Heart Disease dataset (Cleveland + others).
- 📋 **Form Input**: Collects key clinical features (age, sex, chest pain type, blood pressure, cholesterol, fasting blood sugar, ECG results, max heart rate, exercise angina, ST depression, slope, number of major vessels, thalassemia type, country).
- 📂 **Batch Analysis**: Step-by-step workflow with drag‑and‑drop CSV upload, column mapping, auto-cleaning, and progress feedback.
- 📊 **Dashboard & PDF Export**:
  - KPIs: total predictions, positive rate, average risk
  - Risk probability distribution (histogram + KDE)
  - Box plots and numeric-feature correlation heatmap
  - Cluster analysis: distribution bar chart, profiles table, and scatter plot
  - Exports all visuals and records to a styled PDF with table of contents and responsive column widths
- 📑 **Patient PDF Reports**: Generate downloadable patient-level summaries with all inputs, prediction, probability, risk band, and confidence.
- 📚 **Research Paper Viewer**: Renders a bundled LaTeX manuscript with MathJax, tables, figures, and reference links.

- 🎨 **Modern UI**: Responsive Bootstrap 5 theme with custom colors, icons, and charts.
- 🔒 **Safe by design**:
  - CSRF tokens for forms and API
  - Security headers (no-sniff, frame denial, no referrer, no FLoC)
  - 🗄 **Persistence**: SQLite database via SQLAlchemy, storing predictions with metadata.

---

## 🛠 Tech Stack
- **Backend**: Python, Flask, Flask-SQLAlchemy
- **ML**: scikit-learn, pandas, numpy
- **Frontend**: Jinja2 templates, Bootstrap 5, Plotly.js
- **Reports**: ReportLab for PDF export
- **Database**: SQLite (default)

---

## 📂 Project Structure
```text
heart-app/
├── app.py               # Application entry point
├── config.py            # Configuration classes
├── helpers.py           # Shared utility functions
├── outlier_detection.py # Outlier detection helpers
├── admin/               # Admin blueprint
├── auth/                # Authentication blueprint and forms
├── routes/              # Core Flask blueprints
│   ├── __init__.py
│   └── predict.py
├── services/            # Business logic and ML helpers
│   ├── auth.py
│   ├── data.py
│   ├── pdf.py
│   ├── security.py
│   └── simulation.py
├── templates/           # Jinja2 templates
│   ├── base.html
│   ├── error.html
│   └── predict/
│       ├── form.html
│       └── result.html
├── static/              # CSS, images and sample files
│   ├── styles.css
│   ├── logo.svg
│   └── sample.csv
├── ml/                  # Trained model artifacts
│   └── model.pkl
├── superadmin/          # Superadmin blueprint
├── tests/               # Pytest suites
│   ├── test_predict.py
│   └── ...
├── research_paper.tex   # Research paper content
└── requirements.txt     # Python dependencies
```

## 🗺️ Blueprints

- `predict` – renders the prediction form and returns the model's risk assessment.

---

## 🚀 Quickstart

### 1. Clone the repo
```bash
git clone https://github.com/rasikasrimal/heart-disease-risk-app.git
cd heart-disease-risk-app
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and adjust the values for your environment:
```bash
cp .env.example .env
```

### 5. Run the app
```bash
flask run
```
App will run at: http://127.0.0.1:5000

### 6. Run tests
```bash
pytest
```

### Environment variables

The application reads configuration from environment variables (see `.env.example`):

| Variable    | Description                                  | Default                     |
|-------------|----------------------------------------------|-----------------------------|
| `SECRET_KEY`| Flask secret key for sessions                | random value                |
| `DATABASE_URI` | Database connection string                | `sqlite:///instance/app.db` |
| `MODEL_PATH`   | Path to the trained model file            | `ml/model.pkl`              |
| `FLASK_ENV`    | `development` loads `DevelopmentConfig`   | `production`                |

## 📈 Example Workflow

1. **Enter Data** → Open the homepage and fill in patient details through the form.
2. **Batch Predict** → Upload a CSV, map columns, and review cleaned data.
3. **Analyze Trends** → Use the dashboard to explore KPIs and charts.
4. **Export Reports** → Download patient-level PDFs or the full dashboard report.

---

## ⚠️ Disclaimer

This project is provided strictly for **educational and demonstration purposes**.
It is **not a medical device**, and its outputs must **not** be used as a substitute for professional medical advice, diagnosis, or treatment.

