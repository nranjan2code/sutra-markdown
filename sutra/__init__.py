"""
Sutra-Markdown V2

Revolutionary document-to-markdown converter powered by AI embeddings and intelligent routing.

90% cost reduction. 10-50x faster. Superior quality.
"""

__version__ = "2.0.0"
__author__ = "Sutra Team"
__license__ = "MIT"

from sutra.router import SmartRouter, ComplexityAnalyzer
from sutra.converters import ConverterFactory
from sutra.models.document import ParsedDocument, DocumentType  
from sutra.models.result import MarkdownResult, BatchResult
from sutra.models.enums import ConversionTier, QualityLevel

__all__ = [
    "SmartRouter",
    "ComplexityAnalyzer", 
    "ConverterFactory",
    "ParsedDocument", 
    "DocumentType",
    "MarkdownResult",
    "BatchResult",
    "ConversionTier",
    "QualityLevel",
]
