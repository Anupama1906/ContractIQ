from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics import renderPDF
import os
from datetime import datetime

# ── Brand Colours ────────────────────────────────────────────────────────────
PRIMARY      = colors.HexColor("#1E3A5F")   # deep navy
ACCENT       = colors.HexColor("#2563EB")   # blue
SURFACE      = colors.HexColor("#F8FAFC")   # near-white
BORDER       = colors.HexColor("#E2E8F0")   # light grey

RISK_HIGH    = colors.HexColor("#DC2626")
RISK_MED     = colors.HexColor("#F59E0B")
RISK_LOW     = colors.HexColor("#16A34A")

AGENT_COLORS = {
    "legal":       colors.HexColor("#7C3AED"),
    "financial":   colors.HexColor("#2563EB"),
    "compliance":  colors.HexColor("#0D9488"),
    "operational": colors.HexColor("#EA580C"),
    "data":        colors.HexColor("#DC2626"),
    "termination": colors.HexColor("#D97706"),
}

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm


# ── Helpers ──────────────────────────────────────────────────────────────────

def sanitize(text: str) -> str:
    """Strip characters that latin-1 cannot encode."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def risk_color(score: float) -> colors.Color:
    if score >= 0.7:
        return RISK_HIGH
    if score >= 0.4:
        return RISK_MED
    return RISK_LOW


def risk_label(score: float) -> str:
    if score >= 0.7:
        return "HIGH"
    if score >= 0.4:
        return "MEDIUM"
    return "LOW"


def score_bar(score: float, bar_width: float = 120, height: float = 8) -> Drawing:
    """Render a horizontal progress bar for a risk score."""
    d = Drawing(bar_width, height)
    # Background track
    d.add(Rect(0, 0, bar_width, height, fillColor=BORDER, strokeColor=None))
    # Filled portion
    fill_w = max(2, score * bar_width)
    d.add(Rect(0, 0, fill_w, height, fillColor=risk_color(score), strokeColor=None))
    return d


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title", fontSize=28, leading=34,
            textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_CENTER
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontSize=11, leading=16,
            textColor=colors.HexColor("#CBD5E1"), fontName="Helvetica", alignment=TA_CENTER
        ),
        "section_header": ParagraphStyle(
            "section_header", fontSize=13, leading=18,
            textColor=PRIMARY, fontName="Helvetica-Bold", spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body", fontSize=9, leading=14,
            textColor=colors.HexColor("#374151"), fontName="Helvetica"
        ),
        "body_bold": ParagraphStyle(
            "body_bold", fontSize=9, leading=14,
            textColor=colors.HexColor("#111827"), fontName="Helvetica-Bold"
        ),
        "caption": ParagraphStyle(
            "caption", fontSize=8, leading=11,
            textColor=colors.HexColor("#6B7280"), fontName="Helvetica"
        ),
        "tag": ParagraphStyle(
            "tag", fontSize=7, leading=10,
            textColor=colors.white, fontName="Helvetica-Bold", alignment=TA_CENTER
        ),
        "metric_score": ParagraphStyle(
            "metric_score", fontSize=22, leading=26,
            textColor=PRIMARY, fontName="Helvetica-Bold", alignment=TA_CENTER
        ),
        "bullet": ParagraphStyle(
            "bullet", fontSize=9, leading=13,
            textColor=colors.HexColor("#374151"), fontName="Helvetica",
            leftIndent=10, bulletIndent=0
        ),
        "rec_title": ParagraphStyle(
            "rec_title", fontSize=9, leading=13,
            textColor=PRIMARY, fontName="Helvetica-Bold"
        ),
    }


# ── Page Templates ────────────────────────────────────────────────────────────

def _cover_background(canvas, doc):
    """Draw the navy cover band on page 1 only."""
    canvas.saveState()
    if doc.page == 1:
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, PAGE_H - 120 * mm, PAGE_W, 120 * mm, fill=1, stroke=0)
    canvas.restoreState()


def _header_footer(canvas, doc):
    _cover_background(canvas, doc)
    canvas.saveState()

    # Header bar (pages > 1)
    if doc.page > 1:
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, PAGE_H - 14 * mm, PAGE_W, 14 * mm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(colors.white)
        canvas.drawString(MARGIN, PAGE_H - 9 * mm, "ContractIQ  |  Risk Analysis Report")
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 9 * mm,
                               f"CONFIDENTIAL  •  {datetime.now().strftime('%d %b %Y')}")

    # Footer
    canvas.setFillColor(BORDER)
    canvas.rect(0, 0, PAGE_W, 10 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(MARGIN, 3.5 * mm, "For internal review only. Generated by ContractIQ.")
    canvas.drawRightString(PAGE_W - MARGIN, 3.5 * mm, f"Page {doc.page}")

    canvas.restoreState()


# ── Section Builders ──────────────────────────────────────────────────────────

def _cover_section(story, data, s, final_score):
    """Full-width cover block (sits inside the navy band via spacer)."""
    story.append(Spacer(1, 28 * mm))
    story.append(Paragraph("CONTRACT RISK ANALYSIS", s["cover_title"]))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Confidential  •  AI-Powered Risk Intelligence", s["cover_sub"]))
    story.append(Spacer(1, 6 * mm))

    doc_id = sanitize(data.get("document_id", "N/A"))
    date_str = datetime.now().strftime("%d %B %Y, %H:%M")
    story.append(Paragraph(f"Document ID: {doc_id}  •  Generated: {date_str}", s["cover_sub"]))

    story.append(Spacer(1, 30 * mm))

    # Overall score pill
    color = risk_color(final_score)
    label = risk_label(final_score)
    pill_data = [[
        Paragraph(f"{final_score:.2f}", s["metric_score"]),
        Paragraph(f"OVERALL RISK\n{label}", ParagraphStyle(
            "pill_label", fontSize=10, leading=14,
            textColor=color, fontName="Helvetica-Bold"
        )),
    ]]
    pill_table = Table(pill_data, colWidths=[40 * mm, 80 * mm])
    pill_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ("BOX", (0, 0), (-1, -1), 1.5, color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(pill_table)
    story.append(PageBreak())


def _divider(story):
    story.append(Spacer(1, 3 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(Spacer(1, 3 * mm))


def _section_title(story, text, s):
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(sanitize(text), s["section_header"]))
    _divider(story)


def _executive_summary(story, data, s, final_score):
    _section_title(story, "Executive Summary", s)

    report = sanitize(data.get("report", ""))
    summary = ""
    for line in report.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("**") \
                and not stripped.startswith("-") and not stripped.startswith("FINAL"):
            summary = stripped
            break

    story.append(Paragraph(summary or "No summary available.", s["body"]))
    story.append(Spacer(1, 4 * mm))

    # Three KPI boxes
    color = risk_color(final_score)
    kpi_data = [[
        Paragraph(f"{final_score:.2f}", s["metric_score"]),
        Paragraph(risk_label(final_score), s["metric_score"]),
        Paragraph(str(len([k for k in [
            "legal_risk","financial_risk","compliance_risk",
            "operational_risk","data_risk","termination_risk"
        ] if data.get(k, 0) >= 0.7])), s["metric_score"]),
    ], [
        Paragraph("Risk Score", s["caption"]),
        Paragraph("Risk Level", s["caption"]),
        Paragraph("High Risk Areas", s["caption"]),
    ]]
    kpi_table = Table(kpi_data, colWidths=[55 * mm, 55 * mm, 55 * mm])
    kpi_table.setStyle(TableStyle([
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND",   (0, 0), (-1, 0), SURFACE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), color),
        ("BOX",          (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)


def _risk_vector_table(story, data, s):
    _section_title(story, "Risk Vector Breakdown", s)

    metrics = [
        ("legal_risk",       "Legal"),
        ("financial_risk",   "Financial"),
        ("compliance_risk",  "Compliance"),
        ("operational_risk", "Operational"),
        ("data_risk",        "Data & Privacy"),
        ("termination_risk", "Termination"),
    ]

    rows = [["Risk Area", "Score", "Level", "Bar"]]
    for key, label in metrics:
        score = data.get(key, 0.0)
        color = risk_color(score)
        level_para = Paragraph(
            risk_label(score),
            ParagraphStyle("lbl", fontSize=7, fontName="Helvetica-Bold",
                           textColor=colors.white, alignment=TA_CENTER)
        )
        level_cell = Table([[level_para]], colWidths=[18 * mm])
        level_cell.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("ROUNDEDCORNERS", [3, 3, 3, 3]),
        ]))

        rows.append([
            Paragraph(sanitize(label), s["body_bold"]),
            Paragraph(f"{score:.2f}", ParagraphStyle(
                "sc", fontSize=10, fontName="Helvetica-Bold",
                textColor=color, alignment=TA_CENTER)),
            level_cell,
            score_bar(score, bar_width=100),
        ])

    col_w = [55 * mm, 20 * mm, 22 * mm, 65 * mm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, SURFACE]),
        ("INNERGRID",     (0, 0), (-1, -1), 0.3, BORDER),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    story.append(t)


def _detailed_analysis(story, data, s):
    _section_title(story, "Detailed Risk Analysis", s)

    report = sanitize(data.get("report", "No report available."))
    agent_order = ["legal", "financial", "compliance", "operational", "data", "termination"]

    for agent in agent_order:
        key = f"{agent}_risk"
        score = data.get(key, 0.0)
        color = AGENT_COLORS.get(agent, PRIMARY)

        # Agent header row
        header_data = [[
            Paragraph(agent.upper(), ParagraphStyle(
                "ah", fontSize=9, fontName="Helvetica-Bold",
                textColor=colors.white)),
            Paragraph(f"Score: {score:.2f}  |  {risk_label(score)}", ParagraphStyle(
                "as", fontSize=8, fontName="Helvetica",
                textColor=colors.white, alignment=TA_RIGHT)),
        ]]
        header_t = Table(header_data, colWidths=[80 * mm, 85 * mm])
        header_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), color),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (0, 0),   8),
            ("RIGHTPADDING",  (-1, 0), (-1, -1), 8),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(Spacer(1, 3 * mm))
        story.append(header_t)

        # Extract bullet points for this agent from the report markdown
        bullets = []
        in_section = False
        for line in report.split("\n"):
            stripped = line.strip()
            if f"**{agent.title()}" in stripped or f"**{agent.upper()}" in stripped:
                in_section = True
                continue
            if in_section:
                if stripped.startswith("**") and agent.lower() not in stripped.lower():
                    break
                if stripped.startswith("-"):
                    bullets.append(stripped[1:].strip())

        # Fallback: use the comment log if no bullets parsed
        if not bullets:
            bullets = ["See overall report for details."]

        body_rows = [[Paragraph(f"• {sanitize(b)}", s["bullet"])] for b in bullets]
        body_t = Table(body_rows, colWidths=[165 * mm])
        body_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.white),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.3, BORDER),
        ]))
        story.append(body_t)


def _recommendations(story, data, s):
    _section_title(story, "Recommendations", s)

    report = sanitize(data.get("report", ""))
    recs = []
    in_recs = False
    for line in report.split("\n"):
        stripped = line.strip()
        if "recommendation" in stripped.lower() and stripped.startswith("#"):
            in_recs = True
            continue
        if in_recs and stripped and stripped[0].isdigit() and "." in stripped:
            recs.append(stripped)

    if not recs:
        recs = ["Review contract terms with legal counsel before signing."]

    for i, rec in enumerate(recs, 1):
        # Split bold title from body if ** present
        parts = rec.split("**")
        if len(parts) >= 3:
            title = parts[1].strip(" .")
            body = "".join(parts[2:]).strip(" .")
        else:
            title = f"Recommendation {i}"
            body = rec.lstrip("0123456789. ")

        rec_data = [[
            Paragraph(str(i), ParagraphStyle(
                "rn", fontSize=11, fontName="Helvetica-Bold",
                textColor=colors.white, alignment=TA_CENTER)),
            [
                Paragraph(sanitize(title), s["rec_title"]),
                Spacer(1, 2),
                Paragraph(sanitize(body), s["body"]),
            ]
        ]]
        rec_t = Table(rec_data, colWidths=[12 * mm, 153 * mm])
        rec_t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), ACCENT),
            ("BACKGROUND",    (1, 0), (1, 0), SURFACE),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("ALIGN",         (0, 0), (0, 0),  "CENTER"),
            ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING",   (1, 0), (1, 0),   10),
        ]))
        story.append(rec_t)
        story.append(Spacer(1, 2 * mm))


def _footer_section(story, data, s, final_score):
    story.append(Spacer(1, 8 * mm))
    _divider(story)
    color = risk_color(final_score)
    footer_data = [[
        Paragraph(f"FINAL RISK SCORE: {final_score:.2f} / 1.00", ParagraphStyle(
            "fs", fontSize=14, fontName="Helvetica-Bold", textColor=color)),
        Paragraph(
            f"Document ID: {sanitize(data.get('document_id','N/A'))}\n"
            f"Generated: {datetime.now().strftime('%d %B %Y')}",
            s["caption"]),
    ]]
    ft = Table(footer_data, colWidths=[100 * mm, 65 * mm])
    ft.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "RIGHT"),
        ("BACKGROUND",    (0, 0), (-1, -1), SURFACE),
        ("BOX",           (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (0, 0),   10),
        ("RIGHTPADDING",  (1, 0), (1, 0),   10),
    ]))
    story.append(ft)


# ── Public Entry Point ────────────────────────────────────────────────────────

def generate_risk_pdf(data: dict, output_path: str) -> str:
    # De-anonymize report text
    mapping_dict = data.get("mapping_dict", {})
    report = data.get("report", "No detailed report available.")
    for placeholder, original in mapping_dict.items():
        report = report.replace(placeholder, original)
    data = {**data, "report": report}

    final_score = float(data.get("risk_score", 0.0))
    s = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=16 * mm, bottomMargin=14 * mm,
        title="Contract Risk Analysis Report",
        author="ContractIQ",
    )

    story = []
    _cover_section(story, data, s, final_score)
    _executive_summary(story, data, s, final_score)
    _risk_vector_table(story, data, s)
    story.append(PageBreak())
    _detailed_analysis(story, data, s)
    story.append(PageBreak())
    _recommendations(story, data, s)
    _footer_section(story, data, s, final_score)

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return output_path