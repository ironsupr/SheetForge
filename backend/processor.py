import pdfplumber
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts all text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
    """Extracts tables from a PDF file as a list of pages, each containing list of tables (2D lists)."""
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            all_tables.append(tables)
    return all_tables
