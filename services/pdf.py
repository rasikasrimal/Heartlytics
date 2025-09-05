from __future__ import annotations

from io import BytesIO
from typing import Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def generate_prediction_pdf(pred, sex_map: Dict[int, str], yesno: Dict[int, str]) -> BytesIO:
    """Generate a simple PDF report for a prediction."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2 * cm, y, "Heart Disease Prediction Report")
    y -= 1 * cm
    c.setFont("Helvetica", 11)

    lines = [
        f"Report ID: {pred.id}",
        f"Generated: {pred.created_at.strftime('%Y-%m-%d %H:%M UTC')}",
        f"Model Version: {pred.model_version}",
        "",
        f"Patient ID: {pred.id}",
        f"Age: {pred.age}    Sex: {sex_map.get(pred.sex, pred.sex)}",
        f"Country: {pred.country or '-'}",
        f"Chest Pain Type: {pred.chest_pain_type}    ST Slope: {pred.st_slope}",
        f"Resting BP: {pred.resting_bp} mmHg    Cholesterol: {pred.cholesterol} mg/dL",
        f"FBS ≥120 mg/dL: {yesno.get(pred.fasting_blood_sugar, pred.fasting_blood_sugar)}    Max HR: {pred.max_heart_rate} bpm",
        f"Ex Induced Angina: {yesno.get(pred.exercise_angina, pred.exercise_angina)}    ST Depression: {pred.oldpeak}",
        f"Rest ECG: {pred.resting_ecg}    Num Major Vessels: {pred.num_major_vessels}",
        f"Thalassemia: {pred.thalassemia_type}",
        "",
        f"Prediction: {'HEART DISEASE (Positive)' if pred.prediction==1 else 'No Heart Disease (Negative)'}",
        f"Confidence: {round(pred.confidence*100,1)}%",
    ]
    for line in lines:
        c.drawString(2 * cm, y, line)
        y -= 0.8 * cm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf
