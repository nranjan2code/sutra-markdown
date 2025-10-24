"""
Smart Router - Intelligent document routing system

Routes parsed documents to optimal conversion tier based on complexity analysis.
Uses embeddings-based analysis to achieve 90-99% cost reduction.

Components:
- ComplexityAnalyzer: Analyzes document complexity using embeddings
- SmartRouter: Routes documents to Tier 1/2/3 based on analysis
- ConversionTier: Enum for tier types

Tiers:
- Tier 1 (90%): Rule-based conversion for simple documents
- Tier 2 (5%): Spatial-aware conversion for moderate complexity
- Tier 3 (5%): LLM-enhanced conversion for complex documents

Usage:
    from sutra.router import SmartRouter, ComplexityAnalyzer
    
    # Analyze complexity
    analyzer = ComplexityAnalyzer(embeddings_service)
    complexity = await analyzer.analyze(parsed_document)
    
    # Route to optimal tier
    router = SmartRouter()
    tier = router.route(complexity)
    
    # Get appropriate converter
    converter = router.get_converter(tier)
    markdown = await converter.convert(parsed_document)
"""

from .analyzer import ComplexityAnalyzer, ComplexityScore, ComplexityMetrics
from .router import SmartRouter, RoutingDecision
from ..models.enums import ConversionTier

__all__ = [
    "ComplexityAnalyzer",
    "ComplexityScore",
    "ComplexityMetrics",
    "SmartRouter",
    "RoutingDecision",
    "ConversionTier"
]
