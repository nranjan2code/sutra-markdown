"""
Document Parsers - Extract content from various document formats

This module provides parsers for:
- PDF documents (PyMuPDF / pdfplumber)
- Word documents (python-docx)
- PowerPoint presentations (python-pptx)
- Images (OCR support)

All parsers follow a common interface and support:
- Async operations
- Streaming for large files
- Text, tables, images extraction
- Metadata extraction
- Error handling

Usage:
    from sutra.parsers import get_parser
    
    # Auto-detect and parse
    parser = get_parser("document.pdf")
    result = await parser.parse()
    
    # Or use specific parser
    from sutra.parsers.pdf import PDFParser
    parser = PDFParser("document.pdf")
    result = await parser.parse()
"""

from typing import Optional
from pathlib import Path
from .base import BaseParser, ParserResult
from .factory import get_parser, get_supported_formats, is_supported

__all__ = [
    "BaseParser",
    "ParserResult",
    "get_parser",
    "get_supported_formats",
    "is_supported"
]
