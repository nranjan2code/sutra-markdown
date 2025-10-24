/**
 * ConversionResult Component
 * 
 * Displays conversion results with beautiful M3 cards
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Stack,
  IconButton,
  Collapse,
  Button,
  Divider,
} from '@mui/material';
import {
  Download as DownloadIcon,
  ContentCopy as CopyIcon,
  CheckCircle as SuccessIcon,
  Speed as SpeedIcon,
  Storage as CacheIcon,
  ExpandMore as ExpandIcon,
} from '@mui/icons-material';
import type { ConvertResponse } from '@/types';

interface ConversionResultProps {
  result: ConvertResponse;
  filename?: string;
}

export const ConversionResult: React.FC<ConversionResultProps> = ({ result, filename }) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(result.markdown);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([result.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename ? filename.replace(/\.[^/.]+$/, '.md') : 'converted.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'tier1':
      case 'RULE_BASED':
        return 'success';
      case 'tier2':
      case 'SPATIAL_AWARE':
        return 'info';
      case 'tier3':
      case 'LLM_ENHANCED':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'tier1':
      case 'RULE_BASED':
        return 'Rule-Based';
      case 'tier2':
      case 'SPATIAL_AWARE':
        return 'Spatial-Aware';
      case 'tier3':
      case 'LLM_ENHANCED':
        return 'LLM-Enhanced';
      default:
        return tier;
    }
  };

  return (
    <Card
      elevation={2}
      sx={{
        borderRadius: 3,
        transition: 'all 0.3s ease',
        '&:hover': {
          boxShadow: 4,
        },
      }}
    >
      <CardContent>
        <Stack spacing={2}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <SuccessIcon color="success" />
              <Typography variant="titleLarge">Conversion Complete</Typography>
            </Stack>
            <Stack direction="row" spacing={1}>
              <IconButton size="small" onClick={handleCopy} color={copied ? 'success' : 'default'}>
                <CopyIcon fontSize="small" />
              </IconButton>
              <IconButton size="small" onClick={handleDownload} color="primary">
                <DownloadIcon fontSize="small" />
              </IconButton>
            </Stack>
          </Box>

          {/* Stats */}
          <Stack direction="row" spacing={1} flexWrap="wrap">
            <Chip
              label={getTierLabel(result.tier)}
              color={getTierColor(result.tier) as any}
              size="small"
              variant="filled"
            />
            <Chip
              icon={<SpeedIcon />}
              label={`${result.processing_time.toFixed(2)}s`}
              size="small"
              variant="outlined"
            />
            {result.cached && (
              <Chip
                icon={<CacheIcon />}
                label="Cached"
                size="small"
                color="info"
                variant="outlined"
              />
            )}
            <Chip
              label={`Quality: ${(result.quality_score * 100).toFixed(0)}%`}
              size="small"
              variant="outlined"
              color={result.quality_score > 0.9 ? 'success' : 'default'}
            />
          </Stack>

          {/* Metadata */}
          <Stack direction="row" spacing={3}>
            <Box>
              <Typography variant="bodySmall" color="text.secondary">
                Words
              </Typography>
              <Typography variant="titleMedium">{result.word_count.toLocaleString()}</Typography>
            </Box>
            <Box>
              <Typography variant="bodySmall" color="text.secondary">
                Lines
              </Typography>
              <Typography variant="titleMedium">{result.line_count.toLocaleString()}</Typography>
            </Box>
          </Stack>

          {/* Warnings */}
          {result.warnings && result.warnings.length > 0 && (
            <>
              <Divider />
              <Box>
                <Typography variant="titleSmall" color="warning.main" gutterBottom>
                  Warnings ({result.warnings.length})
                </Typography>
                <Stack spacing={0.5}>
                  {result.warnings.slice(0, 3).map((warning, index) => (
                    <Typography key={index} variant="bodySmall" color="text.secondary">
                      • {warning}
                    </Typography>
                  ))}
                  {result.warnings.length > 3 && (
                    <Typography variant="bodySmall" color="primary">
                      +{result.warnings.length - 3} more
                    </Typography>
                  )}
                </Stack>
              </Box>
            </>
          )}

          {/* Preview Toggle */}
          <Button
            onClick={() => setExpanded(!expanded)}
            endIcon={
              <ExpandIcon
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s',
                }}
              />
            }
            fullWidth
            variant="outlined"
          >
            {expanded ? 'Hide' : 'Show'} Markdown Preview
          </Button>

          {/* Markdown Preview */}
          <Collapse in={expanded}>
            <Box
              sx={{
                mt: 2,
                p: 2,
                bgcolor: 'surface.container',
                borderRadius: 2,
                maxHeight: 400,
                overflow: 'auto',
              }}
            >
              <pre
                style={{
                  margin: 0,
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {result.markdown.substring(0, 1000)}
                {result.markdown.length > 1000 && '...\n\n(Showing first 1000 characters)'}
              </pre>
            </Box>
          </Collapse>
        </Stack>
      </CardContent>
    </Card>
  );
};
