/**
 * Component Props Types
 * 
 * TypeScript interface definitions for React components
 */

import type { ReactNode } from 'react';
import type { ConvertResponse } from './api';

export interface FileUploadProps {
  accept?: string;
  maxSize?: number;
  disabled?: boolean;
  loading?: boolean;
  progress?: number;
  selectedFile?: File | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
}

export interface ConversionResultProps {
  result: ConvertResponse | null;
  loading?: boolean;
  error?: string | null;
}

export interface QualityBadgeProps {
  score: number;
  size?: 'small' | 'medium' | 'large';
}

export interface TierBadgeProps {
  tier: number;
  size?: 'small' | 'medium' | 'large';
}

export interface StatsCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
}

export interface MetricsDisplayProps {
  conversionTime?: number;
  qualityScore?: number;
  pageCount?: number;
  tier?: number;
  tokensGenerated?: number;
}