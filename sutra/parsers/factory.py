"""
Parser Factory - Auto-detect and instantiate appropriate parser

Automatically selects the right parser based on file type.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from .base import BaseParser, UnsupportedFormatError
from ..models.enums import DocumentType


def get_parser(
    file_path: str | Path,
    parser_type: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> BaseParser:
    """
    Get appropriate parser for file
    
    Auto-detects file type and returns the correct parser instance.
    
    Args:
        file_path: Path to document
        parser_type: Force specific parser type (pdf, docx, pptx, image)
        options: Parser-specific options
    
    Returns:
        Parser instance
    
    Raises:
        UnsupportedFormatError: If file format not supported
    
    Example:
        >>> parser = get_parser("document.pdf")
        >>> result = await parser.parse()
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Detect file type if not specified
    if parser_type is None:
        ext = file_path.suffix.lower()
        
        if ext == '.pdf':
            parser_type = 'pdf'
        elif ext in ['.doc', '.docx']:
            parser_type = 'docx'
        elif ext in ['.ppt', '.pptx']:
            parser_type = 'pptx'
        elif ext in ['.xls', '.xlsx']:
            parser_type = 'xlsx'
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            parser_type = 'image'
        elif ext in ['.txt', '.md', '.rst']:
            parser_type = 'text'
        elif ext in ['.html', '.htm']:
            parser_type = 'html'
        elif ext == '.csv':
            parser_type = 'csv'
        else:
            raise UnsupportedFormatError(
                f"Unsupported file format: {ext}\n"
                f"Supported formats: .pdf, .docx, .pptx, .xlsx, .jpg, .png, .txt, .html, .csv"
            )
    
    # Import and instantiate appropriate parser
    parser_type = parser_type.lower()
    
    if parser_type == 'pdf':
        from .pdf import PDFParser
        return PDFParser(file_path, options)
    
    elif parser_type in ['docx', 'word', 'doc']:
        from .docx import DOCXParser
        return DOCXParser(file_path, options)
    
    elif parser_type in ['pptx', 'powerpoint', 'ppt']:
        from .pptx import PPTXParser
        return PPTXParser(file_path, options)
    
    elif parser_type in ['xlsx', 'excel', 'xls']:
        from .xlsx import XLSXParser
        return XLSXParser(file_path, options)
    
    elif parser_type == 'image':
        from .image import ImageParser
        return ImageParser(file_path, options)
    
    elif parser_type == 'text':
        from .text import TextParser
        return TextParser(file_path, options)
    
    elif parser_type == 'html':
        from .html import HTMLParser
        return HTMLParser(file_path, options)
    
    elif parser_type == 'csv':
        from .csv import CSVParser
        return CSVParser(file_path, options)
    
    else:
        raise UnsupportedFormatError(
            f"Unknown parser type: {parser_type}\n"
            f"Supported types: pdf, docx, pptx, xlsx, image, text, html, csv"
        )


def get_supported_formats() -> Dict[str, list[str]]:
    """
    Get list of supported file formats
    
    Returns:
        Dict mapping parser types to file extensions
    """
    return {
        "pdf": [".pdf"],
        "docx": [".doc", ".docx"],
        "pptx": [".ppt", ".pptx"],
        "xlsx": [".xls", ".xlsx"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
        "text": [".txt", ".md", ".rst"],
        "html": [".html", ".htm"],
        "csv": [".csv"]
    }


def is_supported(file_path: str | Path) -> bool:
    """
    Check if file format is supported
    
    Args:
        file_path: Path to file
    
    Returns:
        True if format is supported
    """
    ext = Path(file_path).suffix.lower()
    supported = get_supported_formats()
    
    for formats in supported.values():
        if ext in formats:
            return True
    
    return False
