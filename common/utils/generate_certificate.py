
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

GOLD       = HexColor("#C9A84C")
DARK_GOLD  = HexColor("#8B6914")
NAVY       = HexColor("#1A2C5B")
WHITE      = HexColor("#FFFFFF")
LIGHT_GRAY = HexColor("#F5F5F5")
DARK_GRAY  = HexColor("#333333")


def _safe_str(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _draw_border(c, width, height):
    margin = 15 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)
    inner = margin + 4 * mm
    c.setLineWidth(1)
    c.rect(inner, inner, width - 2 * inner, height - 2 * inner)
    for x, y in [
        (margin, margin),
        (width - margin, margin),
        (margin, height - margin),
        (width - margin, height - margin),
    ]:
        c.setFillColor(GOLD)
        c.circle(x, y, 3, fill=1, stroke=0)


def _draw_background(c, width, height):
    c.setFillColor(LIGHT_GRAY)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(0, height - 2 * cm, width, 2 * cm, fill=1, stroke=0)
    c.rect(0, 0, width, 1.5 * cm, fill=1, stroke=0)


def _draw_seal(c, x, y, radius=1.2 * cm):
    c.setFillColor(GOLD)
    c.setStrokeColor(DARK_GOLD)
    c.setLineWidth(1.5)
    c.circle(x, y, radius, fill=1, stroke=1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(x, y - 6, "DA")


def generate_certificate(
    student_name: str,
    course_name: str,
    completion_date: str = None,
    instructor_name: str = "Instructor",
    organization_name: str = "Online Academy",
    certificate_id: str = None,
    duration_hours: int = None,
) -> bytes:
    student_name      = _safe_str(student_name)      or "Student"
    course_name       = _safe_str(course_name)       or "Course"
    instructor_name   = _safe_str(instructor_name)   or "Instructor"
    organization_name = _safe_str(organization_name) or "Online Academy"
    certificate_id    = _safe_str(certificate_id)    or "N/A"

    if not completion_date:
        completion_date = datetime.now().strftime("%d %B %Y")
    completion_date = _safe_str(completion_date)

    buffer = io.BytesIO()
    width, height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=(width, height))

    _draw_background(c, width, height)
    _draw_border(c, width, height)


    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 1.3 * cm, organization_name.upper())


    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 5 * cm, "CERTIFICATE OF COMPLETION")

    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    line_w = 14 * cm
    c.line(width / 2 - line_w / 2, height - 5.5 * cm,
           width / 2 + line_w / 2, height - 5.5 * cm)

    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 6.8 * cm, "This is to certify that")


    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 8.5 * cm, student_name)

    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    name_w = len(student_name) * 10 + 60
    c.line(width / 2 - name_w / 2, height - 9 * cm,
           width / 2 + name_w / 2, height - 9 * cm)

    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 10 * cm,
                        "has successfully completed the course")


    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 11.5 * cm, f'"{course_name}"')

    if duration_hours:
        c.setFillColor(DARK_GRAY)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 12.5 * cm,
                            f"Total Duration: {duration_hours} hours")


    bottom_y = 4 * cm


    c.setFillColor(DARK_GRAY)
    c.setFont("Helvetica", 11)
    c.drawCentredString(width * 0.22, bottom_y + 1.0 * cm, completion_date)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(width * 0.10, bottom_y + 0.6 * cm, width * 0.34, bottom_y + 0.6 * cm)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width * 0.22, bottom_y + 0.2 * cm, "Date of Completion")


    _draw_seal(c, width / 2, bottom_y + 0.9 * cm, radius=1.1 * cm)


    c.setFillColor(NAVY)
    c.setFont("Helvetica-BoldOblique", 13)
    c.drawCentredString(width * 0.78, bottom_y + 1.0 * cm, instructor_name)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.line(width * 0.65, bottom_y + 0.6 * cm, width * 0.91, bottom_y + 0.6 * cm)
    c.setFont("Helvetica", 9)
    c.setFillColor(DARK_GRAY)
    c.drawCentredString(width * 0.78, bottom_y + 0.2 * cm, "Instructor Signature")


    c.setFillColor(WHITE)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, 0.8 * cm, f"Certificate ID: {certificate_id}")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()