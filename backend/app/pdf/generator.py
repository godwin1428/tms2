"""
TMS — PDF Prescription Generator
Professional prescription PDF using ReportLab.
"""
import os
import io
import qrcode
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from ..config import settings


def generate_prescription_pdf(prescription, db=None) -> str:
    """Generate a professional prescription PDF and return the file path."""
    # Ensure output directory exists
    output_dir = os.path.join(settings.UPLOAD_DIR, "prescriptions")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"rx_{prescription.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontSize=20, textColor=colors.HexColor("#0a66b5"),
        spaceAfter=2 * mm, alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#64748b"),
        alignment=TA_CENTER, spaceAfter=4 * mm,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"],
        fontSize=12, textColor=colors.HexColor("#0a66b5"),
        spaceBefore=6 * mm, spaceAfter=3 * mm,
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["Normal"],
        fontSize=10, leading=14,
    )
    small_style = ParagraphStyle(
        "SmallStyle", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#94a3b8"),
    )

    # ── Header ──
    story.append(Paragraph("TMS — Telemedicine Management System", title_style))
    story.append(Paragraph("Digital e-Prescription", subtitle_style))
    story.append(HRFlowable(
        width="100%", thickness=2, color=colors.HexColor("#0a66b5"),
        spaceAfter=5 * mm,
    ))

    # ── Doctor & Patient Info ──
    doctor_name = prescription.doctor.user.name if prescription.doctor and prescription.doctor.user else "Doctor"
    doctor_spec = prescription.doctor.specialization if prescription.doctor else ""
    doctor_qual = prescription.doctor.qualification if prescription.doctor else ""
    patient_name = prescription.patient.user.name if prescription.patient and prescription.patient.user else "Patient"
    patient_age = prescription.patient.age if prescription.patient else "N/A"
    patient_gender = prescription.patient.gender if prescription.patient else "N/A"
    rx_date = prescription.created_at.strftime("%d %b %Y, %I:%M %p") if prescription.created_at else datetime.now().strftime("%d %b %Y, %I:%M %p")

    info_data = [
        [
            Paragraph(f"<b>Doctor:</b> {doctor_name}<br/>{doctor_spec}<br/>{doctor_qual}", body_style),
            Paragraph(f"<b>Patient:</b> {patient_name}<br/>Age: {patient_age} | Gender: {patient_gender}<br/>Date: {rx_date}", body_style),
        ]
    ]
    info_table = Table(info_data, colWidths=["50%", "50%"])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f7ff")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#c5e3fa")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)

    # ── Diagnosis ──
    story.append(Paragraph("Diagnosis", heading_style))
    diagnosis_text = prescription.diagnosis or "N/A"
    story.append(Paragraph(diagnosis_text, body_style))
    if prescription.notes:
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph(f"<i>Notes: {prescription.notes}</i>", small_style))

    # ── Medicines Table ──
    story.append(Paragraph("Prescribed Medicines", heading_style))

    med_header = ["#", "Medicine", "Dosage", "Frequency", "Duration", "Instructions"]
    med_data = [med_header]

    for i, med in enumerate(prescription.medicines, 1):
        med_data.append([
            str(i),
            med.medicine_name or "",
            med.dosage or "",
            med.frequency or "",
            med.duration or "",
            med.instructions or "",
        ])

    if len(med_data) == 1:
        med_data.append(["", "No medicines prescribed", "", "", "", ""])

    med_table = Table(med_data, colWidths=[25, 110, 80, 80, 60, 110])
    med_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0a66b5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(med_table)

    # ── QR Code ──
    story.append(Spacer(1, 8 * mm))
    qr_data = f"TMS-RX-{prescription.id}|{doctor_name}|{patient_name}|{rx_date}"
    qr_img = qrcode.make(qr_data, box_size=3, border=2)
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_table_data = [
        [
            Image(qr_buffer, width=60, height=60),
            Paragraph(
                f"<b>Digitally Verified</b><br/>"
                f"Prescription ID: RX-{prescription.id:04d}<br/>"
                f"Issued by: {doctor_name}<br/>"
                f"Scan QR to verify authenticity",
                small_style,
            ),
        ]
    ]
    qr_table = Table(qr_table_data, colWidths=[70, 400])
    qr_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(qr_table)

    # ── Footer ──
    story.append(Spacer(1, 10 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(
        "This is a computer-generated prescription from TMS — Telemedicine Management System. "
        "No physical signature is required. For any queries, contact your healthcare provider.",
        ParagraphStyle("FooterStyle", parent=styles["Normal"], fontSize=7, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER),
    ))

    doc.build(story)
    return filepath
