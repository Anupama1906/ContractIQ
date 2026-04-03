from fpdf import FPDF
import os

class RiskReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Contract Risk Analysis Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_risk_pdf(data: dict, output_path: str):
    
    # Remap tokens
    mapping_dict = data.get("mapping_dict", {})
    report_text = data.get("report", "No detailed report available.")
    for placeholder, original in mapping_dict.items():
        report_text = report_text.replace(placeholder, original)

    # Sanitize text for fpdf (remove unsupported characters)
    def sanitize(text: str) -> str:
        return text.encode('latin-1', errors='replace').decode('latin-1')

    pdf = RiskReportPDF()
    pdf.add_page()
    
    # Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, sanitize(f"Document ID: {data['document_id']}"), ln=True)
    pdf.cell(0, 10, sanitize(f"Overall Risk Score: {data.get('risk_score', 'N/A')}"), ln=True)
    pdf.ln(5)

    # Risk Breakdown
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Risk Breakdown", ln=True)
    pdf.set_font("Arial", "", 11)
    
    metrics = ["legal_risk", "financial_risk", "compliance_risk", "operational_risk", "data_risk", "termination_risk"]
    for metric in metrics:
        score = data.get(metric, 0.0)
        pdf.cell(0, 8, sanitize(f"- {metric.replace('_', ' ').title()}: {score}"), ln=True)
    
    pdf.ln(10)

    # Detailed Analysis
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detailed Analysis", ln=True)
    pdf.set_font("Arial", "", 11)

    for line in report_text.split('\n'):
        line = sanitize(line)
        if not line.strip():
            pdf.ln(3)
        elif line.startswith('##'):
            pdf.set_font("Arial", "B", 12)
            pdf.multi_cell(0, 8, line.replace('##', '').strip())
            pdf.set_font("Arial", "", 11)
        elif line.startswith('**'):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(0, 8, line.replace('**', '').strip())
            pdf.set_font("Arial", "", 11)
        else:
            pdf.multi_cell(0, 8, line)

    pdf.output(output_path)
    return output_path