/**
 * Health & Stats API Service
 * 
 * Handles health checks and statistics
 */

import apiClient from './client';
import type { HealthResponse, StatsResponse } from '@/types';

export class HealthService {
  /**
   * Get API health status
   */
  static async getHealth(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/');
    return response.data;
  }
  
  /**
   * Get API statistics
   */
  static async getStats(): Promise<StatsResponse> {
    const response = await apiClient.get<StatsResponse>('/stats');
    return response.data;
  }
}
