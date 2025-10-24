/**
 * Conversion API Service
 * 
 * Handles document conversion requests
 */

import apiClient from './client';
import type { ConvertRequest, ConvertResponse, JobResponse, JobStatusResponse } from '@/types';

export class ConversionService {
  /**
   * Convert document synchronously
   */
  static async convert(file: File, options?: ConvertRequest): Promise<ConvertResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options) {
      formData.append('tier', options.tier || '');
      formData.append('use_cache', String(options.use_cache ?? true));
      if (options.options) {
        formData.append('options', JSON.stringify(options.options));
      }
    }
    
    const response = await apiClient.post<ConvertResponse>('/convert', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }
  
  /**
   * Convert document asynchronously
   */
  static async convertAsync(file: File, options?: ConvertRequest): Promise<JobResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (options) {
      formData.append('tier', options.tier || '');
      formData.append('use_cache', String(options.use_cache ?? true));
      if (options.options) {
        formData.append('options', JSON.stringify(options.options));
      }
    }
    
    const response = await apiClient.post<JobResponse>('/convert/async', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }
  
  /**
   * Get job status
   */
  static async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await apiClient.get<JobStatusResponse>(`/jobs/${jobId}`);
    return response.data;
  }
  
  /**
   * Convert multiple documents
   */
  static async convertBatch(
    files: File[],
    options?: ConvertRequest,
    onProgress?: (progress: number) => void
  ): Promise<ConvertResponse[]> {
    const results: ConvertResponse[] = [];
    
    for (let i = 0; i < files.length; i++) {
      try {
        const result = await this.convert(files[i], options);
        results.push(result);
        
        if (onProgress) {
          onProgress(((i + 1) / files.length) * 100);
        }
      } catch (error) {
        console.error(`Failed to convert ${files[i].name}:`, error);
        throw error;
      }
    }
    
    return results;
  }
  
  /**
   * Poll job status until completion
   */
  static async pollJobStatus(
    jobId: string,
    interval: number = 1000,
    onProgress?: (status: JobStatusResponse) => void
  ): Promise<JobStatusResponse> {
    return new Promise((resolve, reject) => {
      const poll = setInterval(async () => {
        try {
          const status = await this.getJobStatus(jobId);
          
          if (onProgress) {
            onProgress(status);
          }
          
          if (status.status === 'completed') {
            clearInterval(poll);
            resolve(status);
          } else if (status.status === 'failed') {
            clearInterval(poll);
            reject(new Error(status.error || 'Job failed'));
          }
        } catch (error) {
          clearInterval(poll);
          reject(error);
        }
      }, interval);
    });
  }
}
