"""
Base Converter - Abstract interface for all converters

Defines the contract that all converter tiers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.document import ParsedDocument
from ..models.enums import ConversionTier, OutputFormat


@dataclass
class ConversionResult:
    """
    Result of document conversion to multiple formats
    
    Attributes:
        markdown: Generated Markdown content (primary output)
        tier: Conversion tier used
        success: Whether conversion succeeded
        quality_score: Estimated quality (0-1)
        processing_time: Time taken (seconds)
        outputs: Dictionary of format -> content for all requested outputs
        metadata: Additional conversion metadata
        warnings: Non-fatal issues encountered
        errors: Fatal errors (if success=False)
        stats: Conversion statistics
        timestamp: When conversion completed
    """
    markdown: str
    tier: ConversionTier
    success: bool
    quality_score: float
    processing_time: float
    outputs: Dict[OutputFormat, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_output(self, format: OutputFormat) -> Optional[str]:
        """Get output in specific format"""
        if format == OutputFormat.MARKDOWN:
            return self.markdown
        return self.outputs.get(format)
    
    def add_output(self, format: OutputFormat, content: str):
        """Add output in specific format"""
        if format == OutputFormat.MARKDOWN:
            self.markdown = content
        else:
            self.outputs[format] = content
    
    @property
    def word_count(self) -> int:
        """Count words in generated Markdown"""
        return len(self.markdown.split())
    
    @property
    def line_count(self) -> int:
        """Count lines in generated Markdown"""
        return len(self.markdown.split('\n'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'markdown': self.markdown,
            'tier': self.tier.value,
            'success': self.success,
            'quality_score': self.quality_score,
            'processing_time': self.processing_time,
            'word_count': self.word_count,
            'line_count': self.line_count,
            'metadata': self.metadata,
            'warnings': self.warnings,
            'errors': self.errors,
            'stats': self.stats,
            'timestamp': self.timestamp.isoformat(),
        }


class BaseConverter(ABC):
    """
    Abstract base class for all document converters
    
    All converter tiers must implement this interface.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize converter
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._stats = {
            'total_conversions': 0,
            'successful_conversions': 0,
            'failed_conversions': 0,
            'total_processing_time': 0.0,
            'average_quality': 0.0,
        }
    
    @abstractmethod
    async def convert(self, document: ParsedDocument, output_formats: Optional[List[OutputFormat]] = None) -> ConversionResult:
        """
        Convert parsed document to multiple output formats
        
        Args:
            document: Parsed document to convert
            output_formats: List of desired output formats (defaults to [OutputFormat.MARKDOWN])
            
        Returns:
            ConversionResult with content in all requested formats
            
        Raises:
            ConversionError: If conversion fails
        """
        pass
    
    @abstractmethod
    def can_convert(self, document: ParsedDocument) -> bool:
        """
        Check if this converter can handle the document
        
        Args:
            document: Document to check
            
        Returns:
            True if converter can handle document
        """
        pass
    
    @property
    @abstractmethod
    def tier(self) -> ConversionTier:
        """Get conversion tier"""
        pass
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        return self._stats.copy()
    
    def _update_stats(self, result: ConversionResult):
        """Update internal statistics"""
        self._stats['total_conversions'] += 1
        if result.success:
            self._stats['successful_conversions'] += 1
        else:
            self._stats['failed_conversions'] += 1
        self._stats['total_processing_time'] += result.processing_time
        
        # Update average quality
        total = self._stats['total_conversions']
        old_avg = self._stats['average_quality']
        self._stats['average_quality'] = (
            (old_avg * (total - 1) + result.quality_score) / total
        )


class ConversionError(Exception):
    """Raised when conversion fails"""
    pass
