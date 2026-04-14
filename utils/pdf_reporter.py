"""
LAYER 3 — UTILS LAYER: PDF Reporter
=====================================
Generates a professional PDF report per test.

Each PDF includes:
  - Test name, status, duration
  - Environment details
  - Steps executed (from a step log)
  - Failure screenshot (if any)
  - API response snapshot (if any)
"""

import allure
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Colour palette ──────────────────────────────────────────────────────────
PASS_COLOR = colors.HexColor("#28a745")
FAIL_COLOR = colors.HexColor("#dc3545")
SKIP_COLOR = colors.HexColor("#ffc107")
HEADER_BG  = colors.HexColor("#1a1a2e")
ROW_ALT    = colors.HexColor("#f8f9fa")
ACCENT     = colors.HexColor("#0366d6")   # GitHub blue


class PdfReporter:
    """
    Generates a per-test PDF report.
    Call generate() at the end of each test (pass or fail).
    """

    def __init__(
        self,
        test_name: str,
        status: str,          # "PASSED" | "FAILED" | "SKIPPED"
        duration_seconds: float,
        steps: list[str] = None,
        screenshot_path: str = None,
        error_message: str = None,
        extra_data: dict = None,
    ):
        self.test_name = test_name
        self.status = status
        self.duration = duration_seconds
        self.steps = steps or []
        self.screenshot_path = screenshot_path
        self.error_message = error_message
        self.extra_data = extra_data or {}
        self.timestamp = datetime.now()

    def generate(self) -> Optional[str]:
        """Generate PDF and attach to Allure. Returns the file path."""
        if not settings.PDF_REPORT_ENABLED:
            return None

        safe_name = self.test_name.replace(" ", "_").replace("/", "_").replace("::", "__")
        ts = self.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{ts}.pdf"
        filepath = settings.PDF_REPORTS_DIR / filename

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        story = []
        styles = getSampleStyleSheet()

        # Header styles
        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            fontSize=16, textColor=colors.white, alignment=TA_CENTER,
            spaceAfter=6,
        )
        section_style = ParagraphStyle(
            "Section", parent=styles["Heading2"],
            fontSize=11, textColor=ACCENT, spaceBefore=12, spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=9, leading=14,
        )
        step_style = ParagraphStyle(
            "Step", parent=styles["Normal"],
            fontSize=8, leading=13, leftIndent=12,
            textColor=colors.HexColor("#333333"),
        )

        # ── Title block ──────────────────────────────────────────────────
        status_color = {"PASSED": PASS_COLOR, "FAILED": FAIL_COLOR}.get(
            self.status, SKIP_COLOR
        )
        header_data = [[Paragraph(f"Test Report — {self.test_name}", title_style)]]
        header_table = Table(header_data, colWidths=[17 * cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
            ("ROWPADDING", (0, 0), (-1, -1), 12),
            ("ROUNDEDCORNERS", [6]),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.4 * cm))

        # ── Summary ──────────────────────────────────────────────────────
        story.append(Paragraph("Summary", section_style))
        summary_rows = [
            ["Status", self.status],
            ["Duration", f"{self.duration:.2f}s"],
            ["Timestamp", self.timestamp.strftime("%Y-%m-%d %H:%M:%S")],
            ["Environment", settings.ENV.upper()],
            ["Browser", settings.BROWSER.capitalize()],
            ["Base URL", settings.BASE_URL],
        ]
        t = Table(summary_rows, colWidths=[5 * cm, 12 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8f0fe")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#333")),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, ROW_ALT]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
            ("ROWPADDING", (0, 0), (-1, -1), 6),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            # Status cell colour
            ("TEXTCOLOR", (1, 0), (1, 0), status_color),
            ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ]))
        story.append(t)

        # ── Steps ────────────────────────────────────────────────────────
        if self.steps:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Test Steps", section_style))
            for i, step_text in enumerate(self.steps, 1):
                story.append(Paragraph(f"{i}. {step_text}", step_style))

        # ── Error ─────────────────────────────────────────────────────────
        if self.error_message:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Error Details", section_style))
            error_style = ParagraphStyle(
                "Error", parent=styles["Code"],
                fontSize=8, textColor=FAIL_COLOR,
                backColor=colors.HexColor("#fff5f5"),
                leftIndent=8, rightIndent=8, spaceAfter=4,
            )
            story.append(Paragraph(self.error_message[:800], error_style))

        # ── Extra data ────────────────────────────────────────────────────
        if self.extra_data:
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Additional Data", section_style))
            for key, value in self.extra_data.items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", body_style))

        # ── Screenshot ────────────────────────────────────────────────────
        if self.screenshot_path and Path(self.screenshot_path).exists():
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph("Failure Screenshot", section_style))
            story.append(HRFlowable(width="100%", thickness=0.3, color=colors.grey))
            story.append(Spacer(1, 0.2 * cm))
            img = RLImage(self.screenshot_path, width=16 * cm, height=9 * cm)
            story.append(img)

        # ── Build ────────────────────────────────────────────────────────
        doc.build(story)
        logger.info(f"PDF report generated: {filepath}")

        # Attach to Allure
        with open(filepath, "rb") as f:
            allure.attach(
                f.read(),
                name=f"PDF Report — {self.test_name}",
                attachment_type=allure.attachment_type.PDF,
            )

        return str(filepath)
