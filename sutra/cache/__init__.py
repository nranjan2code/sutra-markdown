"""
Caching Layer - Intelligent caching for performance optimization

Three-level caching system:
- Document Cache: Cache parsed documents (memory + disk)
- Embedding Cache: Cache embeddings (Redis + disk)
- Result Cache: Cache conversion results (disk)

Features:
- Multi-level caching
- TTL (time-to-live) support
- Cache invalidation
- Size-based eviction
- Statistics tracking
"""

from .base import BaseCache, CacheStats
from .document_cache import DocumentCache
from .embedding_cache import EmbeddingCache
from .result_cache import ResultCache
from .manager import CacheManager

__all__ = [
    'BaseCache',
    'CacheStats',
    'DocumentCache',
    'EmbeddingCache',
    'ResultCache',
    'CacheManager',
]
