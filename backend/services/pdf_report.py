"""PDF report generator for HR ranking reports."""
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import STORAGE_DIR


def generate_hr_ranking_report(
    job_description: str,
    job_summary: str,
    candidates: List[dict],
    output_path: Path,
) -> Path:
    """
    Generate PDF report with job description summary, ranked candidates,
    ATS scores, and missing skills per candidate.
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        name="CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=8,
    )

    elements = []

    # Title
    elements.append(Paragraph("ATS Resume Analyzer - Candidate Ranking Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Job Description Summary
    elements.append(Paragraph("Job Description Summary", heading_style))
    summary_text = job_summary[:1500] if job_summary else job_description[:1500]
    elements.append(Paragraph(summary_text.replace("\n", "<br/>"), styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Ranked Candidate List
    elements.append(Paragraph("Ranked Candidate List", heading_style))
    table_data = [
        ["Rank", "Applicant Name", "ATS Score", "Skill Match %", "Missing Skills"],
    ]
    for i, c in enumerate(candidates, 1):
        # Use applicant_name if available, otherwise candidate_name
        name = c.get("applicant_name") or c.get("candidate_name", "Unknown")
        score = c.get("ats_score", 0)
        skill_pct = c.get("skills_match_pct", 0)
        missing = ", ".join(c.get("missing_skills", [])[:5])
        if len(c.get("missing_skills", [])) > 5:
            missing += "..."
        table_data.append([str(i), name, f"{score:.1f}", f"{skill_pct:.1f}%", missing[:80]])

    t = Table(table_data, colWidths=[0.5 * inch, 1.5 * inch, 0.8 * inch, 1 * inch, 2.7 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]
        )
    )
    elements.append(t)
    elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    return output_path
