"""
Intelligence Layer - High-Performance Local Embeddings

This module provides optimized local embedding services for:
- Document classification and complexity analysis  
- Structure detection and layout understanding
- Semantic fingerprinting for caching
- Batch processing for high-throughput workloads

LOCAL DEPLOYMENT ONLY:
✅ 100% free - unlimited usage, no per-request costs
✅ 100% private - your data never leaves your servers  
✅ High performance - 8-80ms per embedding (GPU/CPU)
✅ Scalable - supports 10K+ concurrent requests
✅ Offline - works without internet connection
✅ Apache 2.0 - fully open source

Usage:
    from sutra.intelligence import get_embedder
    
    # Get optimized embedder (auto-detects hardware)
    embedder = get_embedder()
    
    # Generate embedding (async-compatible)
    embedding = await embedder.embed_text("Your text here")
    
    # Batch processing (highly optimized)
    embeddings = await embedder.embed_batch(["text1", "text2", "text3"])
"""

from .embeddings import EmbeddingService, get_embedder

__all__ = [
    "EmbeddingService",
    "get_embedder"
]
