/**
 * API Type Definitions
 * 
 * TypeScript interfaces matching the FastAPI backend models
 * These ensure type safety across the entire application
 */

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type ConversionTier = 'tier1' | 'tier2' | 'tier3';

export interface ConvertRequest {
  tier?: ConversionTier;
  options?: Record<string, any>;
  use_cache?: boolean;
  async_mode?: boolean;
}

export interface ConvertResponse {
  markdown: string;
  tier: string;
  quality_score: number;
  processing_time: number;
  word_count: number;
  line_count: number;
  cached: boolean;
  warnings: string[];
}

export interface JobResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  message: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: ConvertResponse;
  error?: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  cache_stats?: {
    total_requests: number;
    cache_hits: number;
    cache_misses: number;
    hit_rate: number;
  };
}

export interface StatsResponse {
  total_conversions: number;
  cache_hits: number;
  cache_misses: number;
  hit_rate: number;
  average_processing_time: number;
  tier_distribution: Record<string, number>;
}

export interface UploadProgress {
  filename: string;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
}

export interface BatchResult {
  total: number;
  completed: number;
  failed: number;
  results: ConvertResponse[];
  errors: Array<{ filename: string; error: string }>;
}
