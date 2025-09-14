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


def generate_dashboard_pdf(
    *,
    rows,
    columns,
    include_patient: bool = True,
    include_inputs: bool = True,
    include_results: bool = True,
    include_visuals: bool = True,
    notes: str = "",
    theme: str = "light",
    sex_map: Dict[int, str] | None = None,
    logo_path: str | None = None,
) -> BytesIO:
    import io as _io
    import math as _math
    from datetime import datetime as _dt
    from zoneinfo import ZoneInfo as _ZoneInfo
    import numpy as _np
    import pandas as _pd

    from reportlab.lib import colors as _colors
    from reportlab.lib.pagesizes import A4 as _A4, landscape as _landscape
    from reportlab.lib.units import cm as _cm
    from reportlab.platypus import (
        SimpleDocTemplate as _SimpleDocTemplate,
        Table as _Table,
        TableStyle as _TableStyle,
        Paragraph as _Paragraph,
        Spacer as _Spacer,
        Image as _Image,
        PageBreak as _PageBreak,
    )
    from reportlab.platypus.tableofcontents import TableOfContents as _TableOfContents
    from reportlab.lib.styles import getSampleStyleSheet as _getSampleStyleSheet

    try:
        import matplotlib as _mpl
        _mpl.use("Agg")
        import matplotlib.pyplot as _plt
    except ModuleNotFoundError:
        _plt = None

    # Force light theme styling for PDF clarity
    theme = "light"

    buf = BytesIO()

    class _MyDocTemplate(_SimpleDocTemplate):
        def afterFlowable(self, flowable):
            from reportlab.platypus import Paragraph as __P
            if isinstance(flowable, __P) and flowable.style.name == "Heading1":
                self.notify("TOCEntry", (0, flowable.getPlainText(), self.page))

    doc = _MyDocTemplate(buf, pagesize=_landscape(_A4))
    styles = _getSampleStyleSheet()
    gen_date = _dt.now(_ZoneInfo("Asia/Colombo")).strftime("%Y-%m-%d %H:%M IST")

    def _header_footer(c, _doc):
        width, height = _doc.pagesize
        c.saveState()
        c.setFillColor(_colors.white)
        c.rect(0, 0, width, height, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(_colors.black)
        c.drawString(_cm, height - _cm, "Heartlytics Report")
        if logo_path:
            try:
                c.drawImage(logo_path, width - 3 * _cm, height - 1.5 * _cm, width=2 * _cm,
                            preserveAspectRatio=True, mask="auto")
            except Exception:
                pass
        c.setFont("Helvetica", 9)
        c.drawString(_cm, _cm / 2, f"Generated {gen_date}")
        page = c.getPageNumber()
        c.drawRightString(width - _cm, _cm / 2, f"Page {page}")
        c.restoreState()

    rows_list = list(rows)
    total = len(rows_list)
    pos = sum(getattr(r, "prediction") == 1 for r in rows_list)
    pos_rate = (pos / total * 100) if total else 0
    avg_risk = (
        sum((getattr(r, "confidence") if getattr(r, "prediction") == 1 else 1 - getattr(r, "confidence")) for r in rows_list)
        / total * 100 if total else 0
    )
    # Risk bands (Low <40, Medium 40–69, High ≥70)
    _risks = _np.array([
        (getattr(r, "confidence") if getattr(r, "prediction") == 1 else 1 - getattr(r, "confidence")) * 100
        for r in rows_list
    ]) if rows_list else _np.array([])
    _low_thr, _high_thr = 40.0, 70.0
    _n_low = int((_risks < _low_thr).sum()) if _risks.size else 0
    _n_med = int(((_risks >= _low_thr) & (_risks < _high_thr)).sum()) if _risks.size else 0
    _n_high = int((_risks >= _high_thr).sum()) if _risks.size else 0

    # Risk distribution image (hist + KDE)
    risk_dist_img = None
    if _plt is not None and rows_list:
        risk = _np.array([
            (r.confidence if r.prediction == 1 else 1 - r.confidence) * 100
            for r in rows_list
        ])
        xs = _np.arange(0, 101, 1)
        n = len(risk)
        if n:
            mean = risk.mean(); var = ((risk - mean) ** 2).sum() / n
            sd = _math.sqrt(var) or 1
            bw = 1.06 * sd * (n ** (-1/5))
            ys = []
            for x in xs:
                u = (x - risk) / bw
                ys.append(_np.exp(-0.5 * u * u).sum() / (n * bw * _math.sqrt(2 * _math.pi)))
            fig, ax = _plt.subplots(figsize=(6, 4))
            ax.hist(risk, bins=20, range=(0, 100), density=True, alpha=0.25, color="#3b82f6")
            ax.plot(xs, ys, color="#1d4ed8", linewidth=2)
            ax.set_xlim(0, 100); ax.set_xlabel("Risk %"); ax.set_ylabel("Density")
            ax.set_title("Risk Probability Distribution", fontweight="bold")
            buf_rd = _io.BytesIO(); fig.tight_layout()
            fig.savefig(buf_rd, format="PNG", dpi=150, bbox_inches="tight", transparent=True, facecolor="none", edgecolor="none")
            _plt.close(fig); buf_rd.seek(0)
            # Fit image inside the frame
            max_w, max_h = doc.width - _cm, doc.height - _cm
            img = _Image(buf_rd)
            iw, ih = img.imageWidth, img.imageHeight
            scale = min(max_w / iw, max_h / ih, 1)
            img.drawWidth = iw * scale; img.drawHeight = ih * scale; img.hAlign = "CENTER"
            risk_dist_img = img

    # Build table
    if sex_map is None:
        sex_map = {0: "Female", 1: "Male"}
    col_map = {
        "id": ("ID", lambda r: r.id),
        "patient_name": ("Name", lambda r: getattr(r, "patient_name", "") or ""),
        "age": ("Age", lambda r: r.age),
        "sex": ("Sex", lambda r: sex_map.get(r.sex, r.sex)),
        "chest_pain": ("Chest pain", lambda r: r.chest_pain_type),
        "rest_bp": ("Rest BP", lambda r: r.resting_blood_pressure if hasattr(r, 'resting_blood_pressure') else getattr(r, 'resting_bp', '')),
        "cholesterol": ("Chol", lambda r: r.cholesterol),
        "max_hr": ("Max HR", lambda r: r.max_heart_rate_achieved if hasattr(r, 'max_heart_rate_achieved') else getattr(r, 'max_heart_rate','')),
        "pred_label": ("Pred", lambda r: "Yes" if r.prediction else "No"),
        "risk_pct": ("Risk %", lambda r: f"{round((r.confidence if r.prediction == 1 else 1 - r.confidence) * 100, 1)}%"),
    }
    headers = [col_map[c][0] for c in columns]
    table_data = [headers]
    for r in rows_list:
        table_data.append([col_map[c][1](r) for c in columns])
    max_lengths = [max(len(str(row[i])) for row in table_data) for i in range(len(headers))]
    total_len = sum(max_lengths)
    col_fracs = []
    for h, L in zip(headers, max_lengths):
        frac = L / total_len if total_len else 1 / len(headers)
        if h in ("Chest pain", "Name"):
            frac = max(frac, 0.15)
        elif h in {"ID", "Age", "Sex", "Pred", "Risk %"}:
            frac = max(frac, 0.05)
        col_fracs.append(frac)
    frac_sum = sum(col_fracs)
    col_widths = [doc.width * (f / frac_sum) for f in col_fracs]
    table = _Table(table_data, repeatRows=1, colWidths=col_widths)
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), _colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, _colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_colors.whitesmoke, _colors.lavender]),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
    ]
    for key in ["patient_name", "chest_pain", "sex", "pred_label"]:
        if key in columns:
            idx = columns.index(key)
            table_styles.append(("ALIGN", (idx, 1), (idx, -1), "LEFT"))
    table.setStyle(_TableStyle(table_styles))

    elements = []
    # TOC
    elements.append(_Paragraph("Table of Contents", styles["Title"]))
    toc = _TableOfContents(); toc.levelStyles = [styles["Normal"]]
    elements.append(toc)
    elements.append(_Spacer(1, 0.5 * _cm))
    # Summary
    elements.append(_Paragraph("Predictions Summary", styles["Heading1"]))
    stats_tbl = _Table([
        ["Metric", "Value"],
        ["Total patients", f"{total}"],
        ["Positive rate", f"{pos_rate:.1f}%"],
        ["Average risk probability", f"{avg_risk:.1f}%"],
        ["High risk (≥70%)", f"{_n_high} ({(_n_high/total*100 if total else 0):.1f}%)"],
        ["Medium risk (40–69%)", f"{_n_med} ({(_n_med/total*100 if total else 0):.1f}%)"],
        ["Low risk (<40%)", f"{_n_low} ({(_n_low/total*100 if total else 0):.1f}%)"],
    ], colWidths=[doc.width * 0.45, doc.width * 0.55])
    stats_tbl.setStyle(_TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), _colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.25, _colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_colors.whitesmoke, _colors.lightgrey]),
    ]))
    elements.append(stats_tbl)
    elements.append(_Spacer(1, 0.5 * _cm))
    # Visualizations
    elements.append(_Paragraph("Visualizations", styles["Heading1"]))
    if risk_dist_img is not None:
        elements.append(risk_dist_img)
        elements.append(_Paragraph("Figure: Risk Probability Distribution", styles["Italic"]))
        elements.append(_Spacer(1, 0.25 * _cm))
    # Records
    elements.append(_PageBreak())
    elements.append(_Paragraph("Records", styles["Heading1"]))
    elements.append(table)

    try:
        doc.multiBuild(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    except Exception:
        doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)
    buf.seek(0)
    return buf
