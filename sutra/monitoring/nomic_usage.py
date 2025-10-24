"""
Nomic API Usage Tracking and Monitoring

Tracks all Nomic API calls to help stay within free tier limits and monitor costs.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import json
from pathlib import Path
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Statistics for Nomic API usage"""
    
    # Counters
    text_embeddings: int = 0
    multimodal_embeddings: int = 0
    total_embeddings: int = 0
    
    # Documents processed
    documents_processed: int = 0
    
    # Costs (estimated)
    estimated_cost: float = 0.0
    
    # Timing
    first_call: Optional[datetime] = None
    last_call: Optional[datetime] = None
    
    # Breakdown by day
    daily_usage: Dict[str, int] = field(default_factory=dict)
    
    # Breakdown by document type
    by_document_type: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'text_embeddings': self.text_embeddings,
            'multimodal_embeddings': self.multimodal_embeddings,
            'total_embeddings': self.total_embeddings,
            'documents_processed': self.documents_processed,
            'estimated_cost': self.estimated_cost,
            'first_call': self.first_call.isoformat() if self.first_call else None,
            'last_call': self.last_call.isoformat() if self.last_call else None,
            'daily_usage': self.daily_usage,
            'by_document_type': self.by_document_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UsageStats":
        """Create from dictionary"""
        stats = cls(
            text_embeddings=data.get('text_embeddings', 0),
            multimodal_embeddings=data.get('multimodal_embeddings', 0),
            total_embeddings=data.get('total_embeddings', 0),
            documents_processed=data.get('documents_processed', 0),
            estimated_cost=data.get('estimated_cost', 0.0),
            daily_usage=data.get('daily_usage', {}),
            by_document_type=data.get('by_document_type', {}),
        )
        
        if data.get('first_call'):
            stats.first_call = datetime.fromisoformat(data['first_call'])
        if data.get('last_call'):
            stats.last_call = datetime.fromisoformat(data['last_call'])
        
        return stats


class NomicUsageTracker:
    """
    Track Nomic API usage and provide alerts
    
    Features:
    - Real-time usage tracking
    - Daily/weekly/monthly summaries
    - Free tier limit warnings
    - Cost estimation
    - Usage analytics
    """
    
    # Pricing (approximate - check Nomic docs for latest)
    COST_PER_1K_TEXT_EMBEDDINGS = 0.001  # $0.001 per 1K embeddings
    COST_PER_1K_MULTIMODAL = 0.002  # $0.002 per 1K embeddings
    
    # Free tier limits (check Nomic docs for current limits)
    FREE_TIER_MONTHLY_LIMIT = 100000  # Assumed 100K embeddings/month
    
    # Warning thresholds
    WARNING_THRESHOLD = 0.80  # Warn at 80% of limit
    CRITICAL_THRESHOLD = 0.95  # Critical at 95% of limit
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize usage tracker
        
        Args:
            storage_path: Path to store usage data (default: ./usage_logs/nomic_usage.json)
        """
        self.storage_path = storage_path or Path("./usage_logs/nomic_usage.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing stats
        self.stats = self._load_stats()
        
        # In-memory cache for quick access
        self._session_stats = UsageStats()
        
        # Lock for thread-safe updates
        self._lock = asyncio.Lock()
    
    def _load_stats(self) -> UsageStats:
        """Load usage stats from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                return UsageStats.from_dict(data)
            except Exception as e:
                logger.warning(f"Failed to load usage stats: {e}")
        
        return UsageStats()
    
    def _save_stats(self):
        """Save usage stats to disk"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.stats.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save usage stats: {e}")
    
    async def track_text_embedding(
        self,
        count: int = 1,
        document_type: Optional[str] = None
    ):
        """
        Track text embedding API call
        
        Args:
            count: Number of embeddings generated
            document_type: Type of document being processed
        """
        async with self._lock:
            now = datetime.now()
            today = now.date().isoformat()
            
            # Update counters
            self.stats.text_embeddings += count
            self.stats.total_embeddings += count
            self.stats.documents_processed += 1
            
            # Update cost
            cost = (count / 1000) * self.COST_PER_1K_TEXT_EMBEDDINGS
            self.stats.estimated_cost += cost
            
            # Update timestamps
            if self.stats.first_call is None:
                self.stats.first_call = now
            self.stats.last_call = now
            
            # Update daily usage
            self.stats.daily_usage[today] = self.stats.daily_usage.get(today, 0) + count
            
            # Update by document type
            if document_type:
                self.stats.by_document_type[document_type] = \
                    self.stats.by_document_type.get(document_type, 0) + 1
            
            # Session stats
            self._session_stats.text_embeddings += count
            self._session_stats.total_embeddings += count
            
            # Save periodically
            self._save_stats()
            
            # Check limits
            await self._check_limits()
    
    async def track_multimodal_embedding(
        self,
        count: int = 1,
        document_type: Optional[str] = None
    ):
        """
        Track multimodal embedding API call
        
        Args:
            count: Number of embeddings generated
            document_type: Type of document being processed
        """
        async with self._lock:
            now = datetime.now()
            today = now.date().isoformat()
            
            # Update counters
            self.stats.multimodal_embeddings += count
            self.stats.total_embeddings += count
            self.stats.documents_processed += 1
            
            # Update cost
            cost = (count / 1000) * self.COST_PER_1K_MULTIMODAL
            self.stats.estimated_cost += cost
            
            # Update timestamps
            if self.stats.first_call is None:
                self.stats.first_call = now
            self.stats.last_call = now
            
            # Update daily usage
            self.stats.daily_usage[today] = self.stats.daily_usage.get(today, 0) + count
            
            # Update by document type
            if document_type:
                self.stats.by_document_type[document_type] = \
                    self.stats.by_document_type.get(document_type, 0) + 1
            
            # Session stats
            self._session_stats.multimodal_embeddings += count
            self._session_stats.total_embeddings += count
            
            # Save periodically
            self._save_stats()
            
            # Check limits
            await self._check_limits()
    
    async def _check_limits(self):
        """Check if approaching free tier limits"""
        monthly_usage = self.get_monthly_usage()
        usage_percentage = monthly_usage / self.FREE_TIER_MONTHLY_LIMIT
        
        if usage_percentage >= self.CRITICAL_THRESHOLD:
            logger.critical(
                f"🚨 CRITICAL: Nomic API usage at {usage_percentage:.1%} "
                f"({monthly_usage:,}/{self.FREE_TIER_MONTHLY_LIMIT:,})"
            )
        elif usage_percentage >= self.WARNING_THRESHOLD:
            logger.warning(
                f"⚠️  WARNING: Nomic API usage at {usage_percentage:.1%} "
                f"({monthly_usage:,}/{self.FREE_TIER_MONTHLY_LIMIT:,})"
            )
    
    def get_monthly_usage(self) -> int:
        """Get total embeddings used this month"""
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_total = 0
        for date_str, count in self.stats.daily_usage.items():
            date = datetime.fromisoformat(date_str)
            if date >= month_start:
                monthly_total += count
        
        return monthly_total
    
    def get_daily_usage(self, days: int = 7) -> Dict[str, int]:
        """Get usage for last N days"""
        cutoff = (datetime.now() - timedelta(days=days)).date()
        
        return {
            date: count
            for date, count in self.stats.daily_usage.items()
            if datetime.fromisoformat(date).date() >= cutoff
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary"""
        monthly_usage = self.get_monthly_usage()
        usage_percentage = monthly_usage / self.FREE_TIER_MONTHLY_LIMIT
        remaining = self.FREE_TIER_MONTHLY_LIMIT - monthly_usage
        
        # Calculate average daily usage
        daily_usage = self.get_daily_usage(30)
        avg_daily = sum(daily_usage.values()) / len(daily_usage) if daily_usage else 0
        
        # Estimate days until limit
        days_until_limit = remaining / avg_daily if avg_daily > 0 else float('inf')
        
        return {
            # Overall stats
            'total_embeddings': self.stats.total_embeddings,
            'text_embeddings': self.stats.text_embeddings,
            'multimodal_embeddings': self.stats.multimodal_embeddings,
            'documents_processed': self.stats.documents_processed,
            'estimated_cost': f"${self.stats.estimated_cost:.4f}",
            
            # Monthly tracking
            'monthly_usage': monthly_usage,
            'monthly_limit': self.FREE_TIER_MONTHLY_LIMIT,
            'usage_percentage': f"{usage_percentage:.1%}",
            'remaining': remaining,
            'status': self._get_status(usage_percentage),
            
            # Projections
            'avg_daily_usage': int(avg_daily),
            'days_until_limit': int(days_until_limit) if days_until_limit != float('inf') else 'N/A',
            
            # Session stats
            'session_embeddings': self._session_stats.total_embeddings,
            'session_documents': self._session_stats.documents_processed,
            
            # Breakdown
            'by_document_type': self.stats.by_document_type,
            'last_7_days': self.get_daily_usage(7),
        }
    
    def _get_status(self, usage_percentage: float) -> str:
        """Get status message based on usage"""
        if usage_percentage >= self.CRITICAL_THRESHOLD:
            return "🚨 CRITICAL - Near limit!"
        elif usage_percentage >= self.WARNING_THRESHOLD:
            return "⚠️  WARNING - Approaching limit"
        elif usage_percentage >= 0.50:
            return "📊 MODERATE - Halfway there"
        else:
            return "✅ HEALTHY - Well within limit"
    
    def print_summary(self):
        """Print formatted usage summary"""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("📊 NOMIC API USAGE TRACKER")
        print("="*60)
        
        print(f"\n📈 OVERALL STATS:")
        print(f"  Total Embeddings: {summary['total_embeddings']:,}")
        print(f"  ├─ Text: {summary['text_embeddings']:,}")
        print(f"  └─ Multimodal: {summary['multimodal_embeddings']:,}")
        print(f"  Documents Processed: {summary['documents_processed']:,}")
        print(f"  Estimated Cost: {summary['estimated_cost']}")
        
        print(f"\n📅 THIS MONTH:")
        print(f"  Usage: {summary['monthly_usage']:,} / {summary['monthly_limit']:,} ({summary['usage_percentage']})")
        print(f"  Remaining: {summary['remaining']:,}")
        print(f"  Status: {summary['status']}")
        
        print(f"\n📊 PROJECTIONS:")
        print(f"  Avg Daily: {summary['avg_daily_usage']:,} embeddings/day")
        print(f"  Days Until Limit: {summary['days_until_limit']}")
        
        print(f"\n💻 THIS SESSION:")
        print(f"  Embeddings: {summary['session_embeddings']:,}")
        print(f"  Documents: {summary['session_documents']:,}")
        
        if summary['by_document_type']:
            print(f"\n📄 BY DOCUMENT TYPE:")
            for doc_type, count in sorted(
                summary['by_document_type'].items(), 
                key=lambda x: x[1], 
                reverse=True
            ):
                print(f"  {doc_type}: {count:,}")
        
        print("\n" + "="*60 + "\n")
    
    def reset_session_stats(self):
        """Reset session statistics"""
        self._session_stats = UsageStats()


# Global instance
_tracker: Optional[NomicUsageTracker] = None


def get_tracker() -> NomicUsageTracker:
    """Get global usage tracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = NomicUsageTracker()
    return _tracker


async def track_text_embedding(count: int = 1, document_type: Optional[str] = None):
    """Helper function to track text embedding"""
    tracker = get_tracker()
    await tracker.track_text_embedding(count, document_type)


async def track_multimodal_embedding(count: int = 1, document_type: Optional[str] = None):
    """Helper function to track multimodal embedding"""
    tracker = get_tracker()
    await tracker.track_multimodal_embedding(count, document_type)


def print_usage_summary():
    """Helper function to print usage summary"""
    tracker = get_tracker()
    tracker.print_summary()
