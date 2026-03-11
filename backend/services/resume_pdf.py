"""Convert resume text to PDF for download."""
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text_to_pdf(text: str, output_path: Path) -> Path:
    """Convert plain text resume to PDF."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    elements = []
    for block in text.split("\n\n"):
        lines = block.split("\n")
        safe_lines = [_escape_html(l) for l in lines if l.strip()]
        if not safe_lines:
            elements.append(Spacer(1, 0.1 * inch))
        else:
            para = "<br/>".join(safe_lines)
            elements.append(Paragraph(para, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))
    doc.build(elements)
    return output_path
