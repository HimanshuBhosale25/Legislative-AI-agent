"""Task 1: PDF Text Extraction Module"""

import pdfplumber
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract clean text from Universal Credit Act 2025 PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
    """
    text_content = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text with proper spacing
            page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
            if page_text:
                text_content.append(page_text)
    
    # Join all pages with double newline
    full_text = "\n\n".join(text_content)
    
    # Clean up the text
    full_text = clean_text(full_text)
    
    return full_text


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and formatting issues.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive blank lines
    lines = text.split("\n")
    cleaned_lines = []
    
    for line in lines:
        # Strip whitespace from each line
        line = line.strip()
        if line:  # Only keep non-empty lines
            cleaned_lines.append(line)
    
    # Join lines back together
    cleaned_text = "\n".join(cleaned_lines)
    
    return cleaned_text


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from the PDF.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    with pdfplumber.open(pdf_path) as pdf:
        metadata = pdf.metadata or {}
        
    return {
        "total_pages": len(pdf.pages) if pdf.pages else 0,
        "author": metadata.get("Author", "Unknown"),
        "title": metadata.get("Title", "Unknown"),
        "creation_date": metadata.get("CreationDate", "Unknown"),
    }
