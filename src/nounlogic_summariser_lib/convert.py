from markitdown import MarkItDown

def convert_pdf_to_md(pdf_path):
    """Convert a PDF file to Markdown.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Converted Markdown text.
    """
    md = MarkItDown()
    result = md.convert(pdf_path)
    return result.text_content
