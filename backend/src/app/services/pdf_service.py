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
    pdf = RiskReportPDF()
    pdf.add_page()
    
    # Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Document ID: {data['document_id']}", ln=True)
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
        pdf.cell(0, 8, f"- {metric.replace('_', ' ').title()}: {score}", ln=True)
    
    pdf.ln(10)

    # Main Report (Markdown parsing logic)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Detailed Analysis", ln=True)
    pdf.set_font("Arial", "", 11)
    
    report_text = data.get("report", "No detailed report available.")
    # Basic Markdown-to-PDF logic: Split by lines and handle headers
    for line in report_text.split('\n'):
        if line.startswith('##'):
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