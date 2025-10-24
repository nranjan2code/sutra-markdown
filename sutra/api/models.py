"""
API Models - Pydantic models for request/response

Defines the data structures for the API.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConvertRequest(BaseModel):
    """Request model for document conversion"""
    tier: Optional[str] = Field(None, description="Conversion tier (tier1/tier2/tier3)")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Conversion options")
    use_cache: bool = Field(True, description="Use caching")
    async_mode: bool = Field(False, description="Process asynchronously")
    enable_intelligence: bool = Field(True, description="Enable AI-powered complexity analysis")
    output_formats: List[str] = Field(["markdown"], description="Desired output formats (markdown, json, xml, csv, yaml)")


class ComplexityMetrics(BaseModel):
    """Complexity analysis metrics"""
    structural_score: float = Field(..., description="Structural complexity (0-1)")
    semantic_score: float = Field(..., description="Semantic diversity (0-1)")
    visual_score: float = Field(..., description="Visual layout complexity (0-1)")
    density_score: float = Field(..., description="Content density (0-1)")
    special_score: float = Field(..., description="Special elements score (0-1)")
    layout_type: str = Field(..., description="Layout type detected")
    page_count: int = Field(..., description="Number of pages")
    table_count: int = Field(..., description="Number of tables")
    image_count: int = Field(..., description="Number of images")
    topic_clusters: int = Field(..., description="Number of topic clusters")
    embedding_diversity: float = Field(..., description="Embedding diversity score")
    layout_complexity: float = Field(..., description="Layout complexity score")
    visual_diversity: float = Field(..., description="Visual diversity score")


class ComplexityAnalysis(BaseModel):
    """Complexity analysis results"""
    score: float = Field(..., description="Overall complexity score (0-1)")
    confidence: float = Field(..., description="Analysis confidence (0-1)")
    reasoning: str = Field(..., description="Human-readable reasoning")
    metrics: ComplexityMetrics = Field(..., description="Detailed metrics")


class ConvertResponse(BaseModel):
    """Response model for synchronous conversion"""
    markdown: str = Field(..., description="Converted Markdown")
    outputs: Dict[str, str] = Field(default_factory=dict, description="Additional output formats")
    tier: str = Field(..., description="Conversion tier used")
    quality_score: float = Field(..., description="Quality score (0-1)")
    processing_time: float = Field(..., description="Processing time (seconds)")
    word_count: int = Field(..., description="Word count")
    line_count: int = Field(..., description="Line count")
    cached: bool = Field(..., description="Whether result was cached")
    warnings: List[str] = Field(default_factory=list, description="Warnings")
    complexity_analysis: Optional[ComplexityAnalysis] = Field(None, description="AI complexity analysis results")


class JobResponse(BaseModel):
    """Response model for async job"""
    job_id: str = Field(..., description="Job ID")
    status: JobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Job creation time")
    message: str = Field(..., description="Status message")


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: JobStatus
    progress: float = Field(..., description="Progress (0-1)")
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[ConvertResponse] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    cache_stats: Optional[Dict[str, Any]] = Field(None, description="Cache statistics")


class StatsResponse(BaseModel):
    """Response model for statistics"""
    total_conversions: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    average_processing_time: float
    tier_distribution: Dict[str, int]
