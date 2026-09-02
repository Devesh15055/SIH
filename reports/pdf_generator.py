"""
PDF Audit Verification Report Generator
Generates formal, multi-section PDF audit reports using ReportLab.
Includes Case ID, Timestamp, OCR, MRZ, Forensics, Face, Consistency, Risk Breakdown, and Disclaimer.
Saves PDF files in generated_reports/ and returns raw PDF bytes for Streamlit/API downloads.
"""

import os
import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

REPORTS_DIR = "C:/Users/Hp/OneDrive/Desktop/SIH2/generated_reports"

def generate_pdf_report(screening_result: Dict[str, Any]) -> str:
    """
    Generate PDF audit report file from screening result dictionary.
    Returns absolute filepath of generated PDF.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    case_id = screening_result.get("screening_id", "UNKNOWN")
    pdf_filename = f"SIH2_Report_{case_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E88E5')
    )
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0E1726'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2C3E50')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#7F8C8D')
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("🛡️ AI-Based Fake Identity & Document Screening System", title_style))
    story.append(Paragraph("Smart India Hackathon (SIH26188) — Official Security Audit Report", body_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E88E5'), spaceAfter=10))

    # Case Summary Header Table
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
    risk_score = screening_result.get("overall_risk_score", 0.0)
    decision = screening_result.get("decision", "MANUAL REVIEW")
    risk_scoring = screening_result.get("risk_scoring_result", {})
    risk_class = risk_scoring.get("risk_classification", "MEDIUM RISK")

    meta_data = [
        [Paragraph("<b>Case ID:</b>", body_style), Paragraph(case_id, body_style), Paragraph("<b>Screening Date:</b>", body_style), Paragraph(now_str, body_style)],
        [Paragraph("<b>Problem Statement:</b>", body_style), Paragraph("SIH26188", body_style), Paragraph("<b>Fraud Risk Score:</b>", body_style), Paragraph(f"<b>{risk_score:.1f} / 100</b>", body_style)],
        [Paragraph("<b>Final Classification:</b>", body_style), Paragraph(f"<b>{risk_class}</b>", body_style), Paragraph("<b>Recommended Decision:</b>", body_style), Paragraph(f"<b>{decision}</b>", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[110, 160, 110, 160])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Extracted Identity Data
    story.append(Paragraph("1. Extracted Identity Fields & OCR Confidence", h2_style))
    ocr = screening_result.get("ocr_result", {})
    fields = ocr.get("fields", {})
    
    ocr_data = [
        [Paragraph("<b>Full Name:</b>", body_style), Paragraph(str(fields.get("full_name") or "N/A"), body_style), Paragraph("<b>Doc Number:</b>", body_style), Paragraph(str(fields.get("document_number") or "N/A"), body_style)],
        [Paragraph("<b>Date of Birth:</b>", body_style), Paragraph(str(fields.get("date_of_birth") or "N/A"), body_style), Paragraph("<b>Gender:</b>", body_style), Paragraph(str(fields.get("gender") or "N/A"), body_style)],
        [Paragraph("<b>Nationality:</b>", body_style), Paragraph(str(fields.get("nationality") or "N/A"), body_style), Paragraph("<b>Expiry Date:</b>", body_style), Paragraph(str(fields.get("expiry_date") or "N/A"), body_style)],
        [Paragraph("<b>OCR Confidence:</b>", body_style), Paragraph(f"{ocr.get('confidence', 0.0):.1f}%", body_style), Paragraph("<b>Warnings:</b>", body_style), Paragraph("; ".join(ocr.get("warnings", [])) or "None", body_style)]
    ]
    t_ocr = Table(ocr_data, colWidths=[110, 160, 110, 160])
    t_ocr.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ocr)
    story.append(Spacer(1, 10))

    # Section 2: MRZ & Document Forensics
    story.append(Paragraph("2. MRZ Validation & Visual Forensics", h2_style))
    mrz = screening_result.get("mrz_result", {})
    forensics = screening_result.get("forensics_result", {})

    mrz_status = mrz.get("status_message", "N/A")
    f_risk = forensics.get("risk_level", "LOW")
    f_score = forensics.get("tampering_risk_score", 0.0)

    for_data = [
        [Paragraph("<b>MRZ Status:</b>", body_style), Paragraph(mrz_status, body_style)],
        [Paragraph("<b>Forensics Tampering Level:</b>", body_style), Paragraph(f"{f_risk} (Score: {f_score:.1f}/100)", body_style)],
        [Paragraph("<b>Detected Tampering Indicators:</b>", body_style), Paragraph("; ".join(forensics.get("indicators", [])) or "None", body_style)]
    ]
    t_for = Table(for_data, colWidths=[160, 380])
    t_for.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_for)
    story.append(Spacer(1, 10))

    # Section 3: Biometric Face & Selfie Authenticity
    story.append(Paragraph("3. Biometric Face Verification & Selfie Authenticity", h2_style))
    face = screening_result.get("face_verification_result", {})
    deepfake = screening_result.get("selfie_authenticity_result", {})

    face_data = [
        [Paragraph("<b>Facial Match Verdict:</b>", body_style), Paragraph(face.get("status", "N/A"), body_style), Paragraph("<b>Similarity Score:</b>", body_style), Paragraph(f"{face.get('similarity_score', 0.0):.1f}%", body_style)],
        [Paragraph("<b>Selfie Authenticity Score:</b>", body_style), Paragraph(f"{deepfake.get('authenticity_score', 0.0):.1f}%", body_style), Paragraph("<b>Screening Label:</b>", body_style), Paragraph(deepfake.get("screening_label", "N/A"), body_style)]
    ]
    t_face = Table(face_data, colWidths=[130, 140, 130, 140])
    t_face.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_face)
    story.append(Spacer(1, 10))

    # Section 4: Explainable Risk Factors
    story.append(Paragraph("4. Explainable Risk Factors", h2_style))
    for exp in risk_scoring.get("human_explanation", []):
        story.append(Paragraph(f"• {exp}", body_style))
    story.append(Spacer(1, 12))

    # Section 5: Mandatory Legal & Audit Disclaimer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
    disclaimer_text = (
        "<b>LEGAL DISCLAIMER:</b> This is an AI-assisted screening system and does not constitute absolute proof of fraud "
        "or identity authenticity. All forensic findings, ELA anomaly maps, biometric scores, and risk classifications are "
        "probabilistic indicators intended to assist human auditors during manual verification."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return pdf_path

def get_pdf_bytes(pdf_path: str) -> bytes:
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            return f.read()
    return b""
