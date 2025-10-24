/**
 * UI State Types
 * 
 * Types for application state management
 */

import type { ConvertResponse, JobStatusResponse } from './api';

export interface ConversionState {
  isConverting: boolean;
  result: ConvertResponse | null;
  error: string | null;
  progress: number;
}

export interface JobState {
  jobs: Map<string, JobStatusResponse>;
  activeJobId: string | null;
}

export interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  defaultTier: 'auto' | 'tier1' | 'tier2' | 'tier3';
  useCache: boolean;
  apiBaseUrl: string;
}

export interface NotificationState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}
