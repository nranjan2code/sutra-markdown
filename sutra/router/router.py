"""
Smart Router - Route documents to optimal conversion tier

Routes parsed documents to the appropriate conversion tier based on
complexity analysis. Implements intelligent routing logic to achieve
90-99% cost reduction by using rule-based conversion for most documents.

Routing Logic:
- Tier 1 (Rule-based): Score < 0.3 → Target 90% of documents
- Tier 2 (Spatial-aware): 0.3 ≤ Score < 0.7 → Target 5% of documents
- Tier 3 (LLM-enhanced): Score ≥ 0.7 → Target 5% of documents

Features:
- Intelligent tier assignment
- Cost tracking and optimization
- Fallback strategies
- Performance monitoring
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from ..models.document import ParsedDocument
from ..models.enums import ConversionTier
from .analyzer import ComplexityScore, ComplexityAnalyzer


@dataclass
class RoutingDecision:
    """
    Routing decision with full context
    
    Attributes:
        tier: Selected conversion tier
        complexity_score: Complexity analysis result
        confidence: Confidence in decision (0-1)
        estimated_cost: Estimated processing cost
        estimated_time: Estimated processing time (seconds)
        reasoning: Human-readable explanation
        fallback_tier: Fallback tier if primary fails
        timestamp: When routing decision was made
    """
    tier: ConversionTier
    complexity_score: ComplexityScore
    confidence: float
    estimated_cost: float
    estimated_time: float
    reasoning: str
    fallback_tier: ConversionTier
    timestamp: datetime


class SmartRouter:
    """
    Smart router for document conversion
    
    Routes documents to optimal conversion tier based on complexity.
    Tracks performance and costs to optimize routing over time.
    
    Args:
        cost_limits: Optional cost limits per tier (for tracking)
            - tier1_cost: Cost per document for Tier 1 (default: $0.001)
            - tier2_cost: Cost per document for Tier 2 (default: $0.005)
            - tier3_cost: Cost per document for Tier 3 (default: $0.020)
        
        time_limits: Optional time limits per tier (seconds)
            - tier1_time: Max time for Tier 1 (default: 2.0s)
            - tier2_time: Max time for Tier 2 (default: 5.0s)
            - tier3_time: Max time for Tier 3 (default: 15.0s)
        
        tier_targets: Optional target distribution
            - tier1_target: Target % for Tier 1 (default: 90%)
            - tier2_target: Target % for Tier 2 (default: 5%)
            - tier3_target: Target % for Tier 3 (default: 5%)
    
    Example:
        >>> router = SmartRouter()
        >>> decision = router.route(complexity_score)
        >>> print(f"Tier: {decision.tier.value}")
        >>> print(f"Cost: ${decision.estimated_cost:.4f}")
        >>> print(f"Time: {decision.estimated_time:.1f}s")
    """
    
    def __init__(
        self,
        cost_limits: Optional[Dict[str, float]] = None,
        time_limits: Optional[Dict[str, float]] = None,
        tier_targets: Optional[Dict[str, float]] = None
    ):
        # Cost per document (in dollars)
        self.costs = cost_limits or {
            "tier1": 0.001,   # $0.001 per document
            "tier2": 0.005,   # $0.005 per document
            "tier3": 0.020    # $0.020 per document
        }
        
        # Time per document (in seconds)
        self.times = time_limits or {
            "tier1": 2.0,     # 2 seconds
            "tier2": 5.0,     # 5 seconds
            "tier3": 15.0     # 15 seconds
        }
        
        # Target distribution
        self.targets = tier_targets or {
            "tier1": 0.90,    # 90%
            "tier2": 0.05,    # 5%
            "tier3": 0.05     # 5%
        }
        
        # Statistics tracking
        self.stats = {
            "total_routed": 0,
            "tier1_count": 0,
            "tier2_count": 0,
            "tier3_count": 0,
            "total_cost": 0.0,
            "total_time": 0.0
        }
    
    def route(self, complexity_score: ComplexityScore) -> RoutingDecision:
        """
        Route document to optimal tier
        
        Args:
            complexity_score: Complexity analysis result
        
        Returns:
            RoutingDecision with tier and metadata
        """
        # Get tier from complexity score
        tier = complexity_score.tier
        
        # Determine fallback tier
        fallback_tier = self._get_fallback_tier(tier)
        
        # Estimate cost and time
        estimated_cost = self._estimate_cost(tier, complexity_score)
        estimated_time = self._estimate_time(tier, complexity_score)
        
        # Generate routing reasoning
        reasoning = self._generate_routing_reasoning(
            tier,
            complexity_score,
            estimated_cost,
            estimated_time
        )
        
        # Create decision
        decision = RoutingDecision(
            tier=tier,
            complexity_score=complexity_score,
            confidence=complexity_score.confidence,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            reasoning=reasoning,
            fallback_tier=fallback_tier,
            timestamp=datetime.now()
        )
        
        # Update statistics
        self._update_stats(tier, estimated_cost, estimated_time)
        
        return decision
    
    def route_with_constraints(
        self,
        complexity_score: ComplexityScore,
        max_cost: Optional[float] = None,
        max_time: Optional[float] = None
    ) -> RoutingDecision:
        """
        Route with cost/time constraints
        
        May downgrade tier to meet constraints.
        
        Args:
            complexity_score: Complexity analysis result
            max_cost: Maximum allowed cost
            max_time: Maximum allowed time
        
        Returns:
            RoutingDecision (possibly with downgraded tier)
        """
        # Start with recommended tier
        tier = complexity_score.tier
        
        # Check constraints and downgrade if needed
        while True:
            cost = self._estimate_cost(tier, complexity_score)
            time = self._estimate_time(tier, complexity_score)
            
            # Check if within constraints
            cost_ok = max_cost is None or cost <= max_cost
            time_ok = max_time is None or time <= max_time
            
            if cost_ok and time_ok:
                break
            
            # Try to downgrade
            if tier == ConversionTier.LLM_ENHANCED:
                tier = ConversionTier.SPATIAL_AWARE
            elif tier == ConversionTier.SPATIAL_AWARE:
                tier = ConversionTier.RULE_BASED
            else:
                # Already at lowest tier
                break
        
        # Create decision with potentially downgraded tier
        fallback_tier = self._get_fallback_tier(tier)
        estimated_cost = self._estimate_cost(tier, complexity_score)
        estimated_time = self._estimate_time(tier, complexity_score)
        
        reasoning = self._generate_routing_reasoning(
            tier,
            complexity_score,
            estimated_cost,
            estimated_time
        )
        
        if tier != complexity_score.tier:
            reasoning += f" (Downgraded from {complexity_score.tier.value} due to constraints)"
        
        decision = RoutingDecision(
            tier=tier,
            complexity_score=complexity_score,
            confidence=complexity_score.confidence * 0.8,  # Lower confidence for constrained
            estimated_cost=estimated_cost,
            estimated_time=estimated_time,
            reasoning=reasoning,
            fallback_tier=fallback_tier,
            timestamp=datetime.now()
        )
        
        self._update_stats(tier, estimated_cost, estimated_time)
        
        return decision
    
    def _get_fallback_tier(self, tier: ConversionTier) -> ConversionTier:
        """Get fallback tier if primary fails"""
        if tier == ConversionTier.LLM_ENHANCED:
            return ConversionTier.SPATIAL_AWARE
        elif tier == ConversionTier.SPATIAL_AWARE:
            return ConversionTier.RULE_BASED
        else:
            return ConversionTier.RULE_BASED  # No fallback for Tier 1
    
    def _estimate_cost(
        self,
        tier: ConversionTier,
        complexity_score: ComplexityScore
    ) -> float:
        """
        Estimate processing cost
        
        Base cost adjusted by document complexity
        """
        # Base costs
        base_costs = {
            ConversionTier.RULE_BASED: self.costs["tier1"],
            ConversionTier.SPATIAL_AWARE: self.costs["tier2"],
            ConversionTier.LLM_ENHANCED: self.costs["tier3"]
        }
        
        base_cost = base_costs[tier]
        
        # Adjust for document size (page count)
        page_multiplier = 1.0 + (complexity_score.metrics.page_count / 100)
        
        # Adjust for complexity (more complex = higher cost)
        complexity_multiplier = 1.0 + (complexity_score.score * 0.5)
        
        estimated_cost = base_cost * page_multiplier * complexity_multiplier
        
        return estimated_cost
    
    def _estimate_time(
        self,
        tier: ConversionTier,
        complexity_score: ComplexityScore
    ) -> float:
        """
        Estimate processing time
        
        Base time adjusted by document complexity
        """
        # Base times
        base_times = {
            ConversionTier.RULE_BASED: self.times["tier1"],
            ConversionTier.SPATIAL_AWARE: self.times["tier2"],
            ConversionTier.LLM_ENHANCED: self.times["tier3"]
        }
        
        base_time = base_times[tier]
        
        # Adjust for document size
        page_multiplier = 1.0 + (complexity_score.metrics.page_count / 50)
        
        # Adjust for complexity
        complexity_multiplier = 1.0 + complexity_score.score
        
        estimated_time = base_time * page_multiplier * complexity_multiplier
        
        return estimated_time
    
    def _generate_routing_reasoning(
        self,
        tier: ConversionTier,
        complexity_score: ComplexityScore,
        estimated_cost: float,
        estimated_time: float
    ) -> str:
        """Generate human-readable routing reasoning"""
        tier_names = {
            ConversionTier.RULE_BASED: "Tier 1 (Rule-based)",
            ConversionTier.SPATIAL_AWARE: "Tier 2 (Spatial-aware)",
            ConversionTier.LLM_ENHANCED: "Tier 3 (LLM-enhanced)"
        }
        
        parts = [
            f"Routed to {tier_names[tier]}",
            f"Complexity: {complexity_score.score:.2f}",
            f"Est. cost: ${estimated_cost:.4f}",
            f"Est. time: {estimated_time:.1f}s",
            f"Confidence: {complexity_score.confidence:.0%}"
        ]
        
        return ". ".join(parts) + "."
    
    def _update_stats(self, tier: ConversionTier, cost: float, time: float):
        """Update routing statistics"""
        self.stats["total_routed"] += 1
        
        if tier == ConversionTier.RULE_BASED:
            self.stats["tier1_count"] += 1
        elif tier == ConversionTier.SPATIAL_AWARE:
            self.stats["tier2_count"] += 1
        else:
            self.stats["tier3_count"] += 1
        
        self.stats["total_cost"] += cost
        self.stats["total_time"] += time
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get routing statistics
        
        Returns:
            Dict with statistics and metrics
        """
        total = self.stats["total_routed"]
        
        if total == 0:
            return {
                "total_routed": 0,
                "tier_distribution": {"tier1": 0.0, "tier2": 0.0, "tier3": 0.0},
                "avg_cost": 0.0,
                "avg_time": 0.0,
                "total_cost": 0.0,
                "total_time": 0.0
            }
        
        return {
            "total_routed": total,
            "tier_distribution": {
                "tier1": self.stats["tier1_count"] / total,
                "tier2": self.stats["tier2_count"] / total,
                "tier3": self.stats["tier3_count"] / total
            },
            "tier_counts": {
                "tier1": self.stats["tier1_count"],
                "tier2": self.stats["tier2_count"],
                "tier3": self.stats["tier3_count"]
            },
            "avg_cost": self.stats["total_cost"] / total,
            "avg_time": self.stats["total_time"] / total,
            "total_cost": self.stats["total_cost"],
            "total_time": self.stats["total_time"],
            "vs_target": {
                "tier1": (self.stats["tier1_count"] / total) - self.targets["tier1"],
                "tier2": (self.stats["tier2_count"] / total) - self.targets["tier2"],
                "tier3": (self.stats["tier3_count"] / total) - self.targets["tier3"]
            }
        }
    
    def print_stats(self):
        """Print routing statistics in human-readable format"""
        stats = self.get_stats()
        
        print(f"\n{'='*70}")
        print(f"📊 Smart Router Statistics")
        print(f"{'='*70}")
        print(f"Total Documents Routed: {stats['total_routed']}")
        print(f"\nTier Distribution:")
        print(f"  Tier 1 (Rule-based):    {stats['tier_distribution']['tier1']:.1%} "
              f"({stats['tier_counts']['tier1']} docs) [Target: {self.targets['tier1']:.0%}]")
        print(f"  Tier 2 (Spatial-aware): {stats['tier_distribution']['tier2']:.1%} "
              f"({stats['tier_counts']['tier2']} docs) [Target: {self.targets['tier2']:.0%}]")
        print(f"  Tier 3 (LLM-enhanced):  {stats['tier_distribution']['tier3']:.1%} "
              f"({stats['tier_counts']['tier3']} docs) [Target: {self.targets['tier3']:.0%}]")
        
        print(f"\nCost Metrics:")
        print(f"  Average Cost: ${stats['avg_cost']:.4f} per document")
        print(f"  Total Cost:   ${stats['total_cost']:.2f}")
        
        print(f"\nTime Metrics:")
        print(f"  Average Time: {stats['avg_time']:.2f}s per document")
        print(f"  Total Time:   {stats['total_time']:.1f}s")
        
        print(f"\nTarget Variance:")
        print(f"  Tier 1: {stats['vs_target']['tier1']:+.1%}")
        print(f"  Tier 2: {stats['vs_target']['tier2']:+.1%}")
        print(f"  Tier 3: {stats['vs_target']['tier3']:+.1%}")
        print(f"{'='*70}\n")
    
    def reset_stats(self):
        """Reset routing statistics"""
        self.stats = {
            "total_routed": 0,
            "tier1_count": 0,
            "tier2_count": 0,
            "tier3_count": 0,
            "total_cost": 0.0,
            "total_time": 0.0
        }


# Helper functions
async def analyze_and_route(
    document: ParsedDocument,
    analyzer: ComplexityAnalyzer,
    router: SmartRouter
) -> RoutingDecision:
    """
    Convenience function to analyze and route in one call
    
    Args:
        document: Parsed document
        analyzer: Complexity analyzer
        router: Smart router
    
    Returns:
        RoutingDecision
    """
    complexity = await analyzer.analyze(document)
    decision = router.route(complexity)
    return decision
