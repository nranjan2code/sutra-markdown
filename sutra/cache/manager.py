"""
Cache Manager - Unified interface for all caches

Provides single entry point for caching operations
across documents, embeddings, and results.

Features:
- Unified cache interface
- Statistics aggregation
- Bulk operations
- Cache warming
"""

from typing import Optional, Dict, Any
import numpy as np

from ..models.document import ParsedDocument
from ..converters.base import ConversionResult
from ..models.enums import ConversionTier

from .document_cache import DocumentCache
from .embedding_cache import EmbeddingCache
from .result_cache import ResultCache


class CacheManager:
    """
    Unified cache manager for all cache types
    """
    
    def __init__(
        self,
        enable_document_cache: bool = True,
        enable_embedding_cache: bool = True,
        enable_result_cache: bool = True,
        cache_dir: Optional[str] = None,
        redis_url: Optional[str] = None
    ):
        """
        Initialize cache manager
        
        Args:
            enable_document_cache: Enable document caching
            enable_embedding_cache: Enable embedding caching
            enable_result_cache: Enable result caching
            cache_dir: Base cache directory
            redis_url: Redis URL for embedding cache
        """
        self.document_cache: Optional[DocumentCache] = None
        self.embedding_cache: Optional[EmbeddingCache] = None
        self.result_cache: Optional[ResultCache] = None
        
        if enable_document_cache:
            doc_dir = f"{cache_dir}/documents" if cache_dir else None
            self.document_cache = DocumentCache(cache_dir=doc_dir)
        
        if enable_embedding_cache:
            emb_dir = f"{cache_dir}/embeddings" if cache_dir else None
            self.embedding_cache = EmbeddingCache(
                cache_dir=emb_dir,
                redis_url=redis_url
            )
        
        if enable_result_cache:
            res_dir = f"{cache_dir}/results" if cache_dir else None
            self.result_cache = ResultCache(cache_dir=res_dir)
    
    # Document cache methods
    async def get_document(self, file_path: str) -> Optional[ParsedDocument]:
        """Get cached parsed document"""
        if not self.document_cache:
            return None
        key = self.document_cache.get_key(file_path)
        return await self.document_cache.get(key)
    
    async def set_document(self, file_path: str, document: ParsedDocument) -> bool:
        """Cache parsed document"""
        if not self.document_cache:
            return False
        key = self.document_cache.get_key(file_path)
        return await self.document_cache.set(key, document)
    
    # Embedding cache methods
    async def get_embedding(
        self,
        text: str,
        model: str = "nomic-embed-text-v1.5"
    ) -> Optional[np.ndarray]:
        """Get cached embedding"""
        if not self.embedding_cache:
            return None
        key = self.embedding_cache.get_key(text, model)
        return await self.embedding_cache.get(key)
    
    async def set_embedding(
        self,
        text: str,
        embedding: np.ndarray,
        model: str = "nomic-embed-text-v1.5"
    ) -> bool:
        """Cache embedding"""
        if not self.embedding_cache:
            return False
        key = self.embedding_cache.get_key(text, model)
        return await self.embedding_cache.set(key, embedding)
    
    # Result cache methods
    async def get_result(
        self,
        file_path: str,
        tier: ConversionTier,
        options: Optional[Dict[str, Any]] = None
    ) -> Optional[ConversionResult]:
        """Get cached conversion result"""
        if not self.result_cache:
            return None
        key = self.result_cache.get_key(file_path, tier.value, options)
        return await self.result_cache.get(key)
    
    async def set_result(
        self,
        file_path: str,
        tier: ConversionTier,
        result: ConversionResult,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Cache conversion result"""
        if not self.result_cache:
            return False
        key = self.result_cache.get_key(file_path, tier.value, options)
        return await self.result_cache.set(key, result)
    
    # Bulk operations
    async def clear_all(self) -> Dict[str, int]:
        """Clear all caches"""
        counts = {}
        
        if self.document_cache:
            counts['documents'] = await self.document_cache.clear()
        
        if self.embedding_cache:
            counts['embeddings'] = await self.embedding_cache.clear()
        
        if self.result_cache:
            counts['results'] = await self.result_cache.clear()
        
        return counts
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from all caches"""
        stats = {}
        
        if self.document_cache and self.document_cache.stats:
            stats['documents'] = self.document_cache.stats.to_dict()
        
        if self.embedding_cache and self.embedding_cache.stats:
            stats['embeddings'] = self.embedding_cache.stats.to_dict()
        
        if self.result_cache and self.result_cache.stats:
            stats['results'] = self.result_cache.stats.to_dict()
        
        # Calculate totals
        if stats:
            total_hits = sum(s.get('hits', 0) for s in stats.values())
            total_misses = sum(s.get('misses', 0) for s in stats.values())
            total_size = sum(s.get('size_bytes', 0) for s in stats.values())
            
            stats['total'] = {
                'hits': total_hits,
                'misses': total_misses,
                'hit_rate': total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0.0,
                'size_bytes': total_size,
                'size_mb': total_size / (1024 * 1024),
            }
        
        return stats
