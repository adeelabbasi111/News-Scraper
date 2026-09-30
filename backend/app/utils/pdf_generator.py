from fpdf import FPDF
import re
import os

def generate_pdf_script(topic: str, content_type: str, script_text: str, filename: str) -> str:
    """
    Generates a formatted PDF of the script.
    Since Roman Urdu is just English characters, standard fonts work perfectly.
    Returns the absolute path to the generated PDF.
    """
    class ScriptPDF(FPDF):
        def header(self):
            # Arial bold 15
            self.set_font('helvetica', 'B', 15)
            # Title
            self.cell(0, 10, 'AI News Script Generator', border=False, align='C')
            self.ln(15)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    pdf = ScriptPDF()
    pdf.add_page()
    
    # Metadata
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, f'Topic: {topic}', ln=True)
    pdf.cell(0, 10, f'Format: {content_type.replace("_", " ").title()}', ln=True)
    pdf.ln(5)
    
    # Script Header
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(200, 50, 50)  # Reddish
    pdf.cell(0, 10, 'FINAL SCRIPT (Roman Urdu):', ln=True)
    pdf.ln(5)
    
    # Script Body
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', '', 12)
    
    # Handle utf-8 encoding safely for basic PDF fonts
    clean_text = script_text.replace('’', "'").replace('‘', "'")
    clean_text = clean_text.replace('"', '"').replace('"', '"')
    clean_text = clean_text.replace('—', '-').replace('–', '-')
    # Catch any remaining non-latin-1 characters
    clean_text = clean_text.encode('latin-1', 'ignore').decode('latin-1')
    
    # Add text with automatic line breaks
    pdf.multi_cell(0, 8, clean_text)
    
    # Ensure exports directory exists in the main app folder
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filepath = os.path.join(export_dir, filename)
    pdf.output(filepath)
    return filepath
