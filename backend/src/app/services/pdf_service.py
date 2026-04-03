from fpdf import FPDF
import os
import re
import textwrap

class RiskReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Contract Risk Analysis Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def normalize_text_for_pdf(text: str, max_word_length: int = 90) -> str:
    """Ensure no unbreakable tokens are longer than max_word_length."""
    # Replace tabs with spaces for consistent width behavior
    text = text.replace("\t", " ")

    def _break_long_token(match):
        token = match.group(0)
        return "\n".join(textwrap.wrap(token, max_word_length))

    return re.sub(r"\S{" + str(max_word_length + 1) + r",}", _break_long_token, text)


def sanitize_line_for_pdf(pdf: FPDF, text: str) -> str:
    """Ensure each character is renderable and not wider than available space."""
    normalized = text.replace("\r", "")
    available_width = pdf.w - pdf.r_margin - pdf.x

    safe_chars = []
    for char in normalized:
        # convert unsupported chars to a placeholder
        try:
            char_width = pdf.get_string_width(char)
        except Exception:
            char = "?"
            char_width = pdf.get_string_width(char)

        if char == "\n":
            safe_chars.append(char)
            continue

        if char_width > available_width:
            safe_chars.append("?")
        else:
            safe_chars.append(char)

    return ''.join(safe_chars)

def _pdf_safe_multi_cell(pdf: FPDF, text: str, h: float = 8, **kwargs):
    """Wrap pdf.multi_cell to avoid x position persisting at right margin."""
    try:
        pdf.multi_cell(0, h, text, **kwargs)
    except Exception:
        # fallback to force character wrapping and replace unsafe chars
        fallback = ''.join(
            c if pdf.get_string_width(c) <= pdf.w - pdf.r_margin - pdf.l_margin else '?'
            for c in text
        )
        pdf.multi_cell(0, h, fallback, **kwargs)
    finally:
        pdf.set_x(pdf.l_margin)


def generate_risk_pdf(data: dict, output_path: str):
    pdf = RiskReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Document ID: {data.get('document_id', 'UNKNOWN')}", ln=True)
    pdf.cell(0, 10, f"Overall Risk Score: {data.get('risk_score', 'N/A')}", ln=True)
    pdf.ln(5)

    # Risk Metrics Table-like display
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Risk Breakdown", ln=True)
    pdf.set_font("Arial", "", 11)
    
    # Mapping details if available
    metrics = ["legal_risk", "financial_risk", "compliance_risk", "operational_risk", "data_risk", "termination_risk"]
    for metric in metrics:
        score = data.get(metric, 0.0)
        _pdf_safe_multi_cell(pdf, f"- {metric.replace('_', ' ').title()}: {score}", wrapmode='CHAR')
    
    pdf.ln(10)

    # Main Report (Markdown parsing logic)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detailed Analysis", ln=True)
    pdf.set_font("Arial", "", 11)
    
    report_text = normalize_text_for_pdf(data.get("report", "No detailed report available."), max_word_length=70)
    # Basic Markdown-to-PDF logic: Split by lines and handle headers
    for line in report_text.split('\n'):
        line = normalize_text_for_pdf(line, max_word_length=70)
        line = sanitize_line_for_pdf(pdf, line)

        if line.startswith('##'):
            pdf.set_font("Arial", "B", 12)
            candidate = sanitize_line_for_pdf(pdf, line.replace('##', '').strip())
            _pdf_safe_multi_cell(pdf, candidate, wrapmode='CHAR')
            pdf.set_font("Arial", "", 11)
        elif line.startswith('**'):
            pdf.set_font("Arial", "B", 11)
            candidate = sanitize_line_for_pdf(pdf, line.replace('**', '').strip())
            _pdf_safe_multi_cell(pdf, candidate, wrapmode='CHAR')
            pdf.set_font("Arial", "", 11)
        else:
            _pdf_safe_multi_cell(pdf, line, wrapmode='CHAR')

    pdf.output(output_path)
    return output_path