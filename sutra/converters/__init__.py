"""
Converters - Transform parsed documents to Markdown

Three-tier conversion system:
- Tier 1: Rule-based (fast, 90% of documents)
- Tier 2: Spatial-aware (layout analysis, 5% of documents)
- Tier 3: LLM-enhanced (highest quality, 5% of documents)
"""

from .base import BaseConverter, ConversionResult
from .tier1 import Tier1Converter
from .tier2 import Tier2Converter
from .tier3 import Tier3Converter
from .factory import ConverterFactory, convert_document

__all__ = [
    'BaseConverter',
    'ConversionResult',
    'Tier1Converter',
    'Tier2Converter',
    'Tier3Converter',
    'ConverterFactory',
    'convert_document',
]
