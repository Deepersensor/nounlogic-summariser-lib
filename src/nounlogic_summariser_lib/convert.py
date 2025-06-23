from pdfplumber import open as pdf_open
from markdownify import markdownify as mdify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def convert_pdf_to_md(pdf_path):
    """Convert a PDF file to Markdown.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        str: Converted Markdown text.
    """
    with pdf_open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    markdown_text = mdify(text)
    return markdown_text

def convert_txt_to_pdf(txt_path, pdf_path):
    """Convert a TXT file to PDF."""
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    y = height - 40
    for line in lines:
        c.drawString(40, y, line.strip())
        y -= 15
        if y < 40:
            c.showPage()
            y = height - 40
    c.save()

def extract_to_markdown(txt_path, md_path):
    """Extract text file to Markdown (plain text as .md)."""
    with open(txt_path, 'r', encoding='utf-8') as fin, open(md_path, 'w', encoding='utf-8') as fout:
        fout.write(fin.read())
