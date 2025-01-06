from pdfplumber import open as pdf_open
from markdownify import markdownify as mdify

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
