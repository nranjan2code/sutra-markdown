"""
Converter Factory - Intelligent converter selection and orchestration

Provides simple interface for document conversion with automatic
tier selection based on complexity analysis or explicit routing.

Usage:
    # Automatic tier selection
    result = await convert_document(document)
    
    # Explicit tier selection
    factory = ConverterFactory()
    converter = factory.get_converter(ConversionTier.RULE_BASED)
    result = await converter.convert(document)
"""

from typing import Dict, Any, Optional, List
import time

from ..models.document import ParsedDocument
from ..models.enums import ConversionTier
from .base import BaseConverter, ConversionResult, ConversionError
from .tier1 import Tier1Converter
from .tier2 import Tier2Converter
from .tier3 import Tier3Converter


class ConverterFactory:
    """
    Factory for creating and managing document converters
    
    Provides intelligent converter selection and caching.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize converter factory
        
        Args:
            config: Configuration for all converters
        """
        self.config = config or {}
        self._converters: Dict[ConversionTier, BaseConverter] = {}
        self._stats = {
            'total_conversions': 0,
            'tier1_conversions': 0,
            'tier2_conversions': 0,
            'tier3_conversions': 0,
            'total_time': 0.0,
            'total_cost': 0.0,
        }
    
    def get_converter(self, tier: ConversionTier) -> BaseConverter:
        """
        Get converter for specified tier
        
        Args:
            tier: Conversion tier
            
        Returns:
            Converter instance for that tier
        """
        # Return cached converter if available
        if tier in self._converters:
            return self._converters[tier]
        
        # Create new converter
        if tier == ConversionTier.RULE_BASED:
            converter = Tier1Converter(self.config)
        elif tier == ConversionTier.SPATIAL_AWARE:
            converter = Tier2Converter(self.config)
        elif tier == ConversionTier.LLM_ENHANCED:
            converter = Tier3Converter(self.config)
        else:
            raise ValueError(f"Unknown conversion tier: {tier}")
        
        # Cache converter
        self._converters[tier] = converter
        return converter
    
    def select_tier(self, document: ParsedDocument) -> ConversionTier:
        """
        Automatically select best conversion tier for document
        
        Args:
            document: Document to analyze
            
        Returns:
            Recommended conversion tier
        """
        # Check if complexity score is available from prior analysis
        complexity = document.metadata.extra.get('complexity_score')
        
        if complexity is not None:
            # Use complexity score for decision
            if complexity < 0.3:
                return ConversionTier.RULE_BASED
            elif complexity < 0.7:
                return ConversionTier.SPATIAL_AWARE
            else:
                return ConversionTier.LLM_ENHANCED
        
        # Fallback: check each converter's can_convert method
        tier3 = self.get_converter(ConversionTier.LLM_ENHANCED)
        if tier3.can_convert(document):
            return ConversionTier.LLM_ENHANCED
        
        tier2 = self.get_converter(ConversionTier.SPATIAL_AWARE)
        if tier2.can_convert(document):
            return ConversionTier.SPATIAL_AWARE
        
        # Default to Tier 1
        return ConversionTier.RULE_BASED
    
    async def select_tier_async(self, document: ParsedDocument, force_analysis: bool = False) -> ConversionTier:
        """
        Asynchronously select best conversion tier using AI complexity analysis
        
        Args:
            document: Document to analyze
            force_analysis: Force new complexity analysis even if cached
            
        Returns:
            Recommended conversion tier with AI-powered analysis
        """
        # Check if complexity score is available from prior analysis (unless forced)
        if not force_analysis:
            complexity = document.metadata.extra.get('complexity_score')
            if complexity is not None:
                return self._tier_from_complexity(complexity)
        
        try:
            # Perform AI-powered complexity analysis
            from ..intelligence.embeddings import get_embedder
            from ..router.analyzer import ComplexityAnalyzer
            
            embedder = get_embedder()
            analyzer = ComplexityAnalyzer(embedder)
            complexity_result = await analyzer.analyze(document)
            
            # Cache complexity analysis results
            document.metadata.extra['complexity_score'] = complexity_result.score
            document.metadata.extra['complexity_analysis'] = {
                'tier': complexity_result.tier.value,
                'confidence': complexity_result.confidence,
                'reasoning': complexity_result.reasoning,
                'layout_type': complexity_result.metrics.column_detection,
                'semantic_diversity': complexity_result.metrics.semantic_score,
                'visual_complexity': complexity_result.metrics.visual_score
            }
            
            return complexity_result.tier
            
        except Exception as e:
            # Log error and fallback to heuristic selection
            print(f"⚠️ AI complexity analysis failed: {e}")
            return self.select_tier(document)
    
    def _tier_from_complexity(self, complexity: float) -> ConversionTier:
        """Convert complexity score to tier"""
        if complexity < 0.3:
            return ConversionTier.RULE_BASED
        elif complexity < 0.7:
            return ConversionTier.SPATIAL_AWARE
        else:
            return ConversionTier.LLM_ENHANCED
    
    async def convert(
        self,
        document: ParsedDocument,
        tier: Optional[ConversionTier] = None,
        enable_ai_analysis: bool = True
    ) -> ConversionResult:
        """
        Convert document to Markdown with intelligent tier selection
        
        Args:
            document: Document to convert
            tier: Optional explicit tier selection (auto-select if None)
            enable_ai_analysis: Use AI-powered complexity analysis for tier selection
            
        Returns:
            Conversion result with Markdown and metadata
        """
        start_time = time.time()
        
        # Select tier if not specified
        if tier is None:
            if enable_ai_analysis:
                tier = await self.select_tier_async(document)
            else:
                tier = self.select_tier(document)
        
        # Get converter
        converter = self.get_converter(tier)
        
        # Convert
        result = await converter.convert(document)
        
        # Update stats
        processing_time = time.time() - start_time
        self._update_stats(tier, processing_time, result)
        
        return result
    
    def _update_stats(
        self,
        tier: ConversionTier,
        processing_time: float,
        result: ConversionResult
    ):
        """Update conversion statistics"""
        self._stats['total_conversions'] += 1
        self._stats['total_time'] += processing_time
        
        # Tier-specific counts
        if tier == ConversionTier.RULE_BASED:
            self._stats['tier1_conversions'] += 1
            self._stats['total_cost'] += 0.001
        elif tier == ConversionTier.SPATIAL_AWARE:
            self._stats['tier2_conversions'] += 1
            self._stats['total_cost'] += 0.005
        elif tier == ConversionTier.LLM_ENHANCED:
            self._stats['tier3_conversions'] += 1
            self._stats['total_cost'] += 0.020
    
    @property
    def stats(self) -> Dict[str, Any]:
        """Get conversion statistics"""
        stats = self._stats.copy()
        
        # Calculate distributions
        total = stats['total_conversions']
        if total > 0:
            stats['tier1_percentage'] = (stats['tier1_conversions'] / total) * 100
            stats['tier2_percentage'] = (stats['tier2_conversions'] / total) * 100
            stats['tier3_percentage'] = (stats['tier3_conversions'] / total) * 100
            stats['average_time'] = stats['total_time'] / total
            stats['average_cost'] = stats['total_cost'] / total
        else:
            stats['tier1_percentage'] = 0.0
            stats['tier2_percentage'] = 0.0
            stats['tier3_percentage'] = 0.0
            stats['average_time'] = 0.0
            stats['average_cost'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reset conversion statistics"""
        self._stats = {
            'total_conversions': 0,
            'tier1_conversions': 0,
            'tier2_conversions': 0,
            'tier3_conversions': 0,
            'total_time': 0.0,
            'total_cost': 0.0,
        }


# Convenience function for simple usage
async def convert_document(
    document: ParsedDocument,
    tier: Optional[ConversionTier] = None,
    config: Optional[Dict[str, Any]] = None,
    output_formats: Optional[List[Any]] = None
) -> ConversionResult:
    """
    Convert document to multiple output formats (convenience function)
    
    Args:
        document: Parsed document to convert
        tier: Optional explicit tier selection
        config: Optional configuration
        output_formats: List of desired output formats
        
    Returns:
        Conversion result with content in all requested formats
        
    Example:
        from sutra.parsers import get_parser
        from sutra.converters import convert_document
        from sutra.models.enums import OutputFormat
        
        # Parse document
        parser = get_parser("document.pdf")
        doc = await parser.parse()
        
        # Convert to multiple formats
        result = await convert_document(
            doc, 
            output_formats=[OutputFormat.MARKDOWN, OutputFormat.JSON]
        )
        print(result.markdown)
        print(result.outputs[OutputFormat.JSON])
    """
    factory = ConverterFactory(config)
    converter = factory.get_converter(tier or ConversionTier.RULE_BASED)
    return await converter.convert(document, output_formats)
