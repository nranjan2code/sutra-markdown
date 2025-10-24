/**
 * Home Page
 * 
 * Main conversion interface with beautiful M3 design
 */

import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
} from '@mui/material';
import { FileUpload, ConversionResult } from '@/components';
import { ConversionService } from '@/services';
import type { ConvertResponse, ConversionTier } from '@/types';

export const HomePage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [tier, setTier] = useState<ConversionTier | 'auto'>('auto');
  const [useCache, setUseCache] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ConvertResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
  };

  const handleFileRemove = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const handleConvert = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const convertResult = await ConversionService.convert(file, {
        tier: tier === 'auto' ? undefined : tier,
        use_cache: useCache,
      });
      setResult(convertResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Conversion failed');
    } finally {
      setLoading(false);
    }
  };

  // Auto-convert when file is selected
  React.useEffect(() => {
    if (file && !result) {
      handleConvert();
    }
  }, [file]);

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Stack spacing={4}>
        {/* Header */}
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="displaySmall" gutterBottom sx={{ fontWeight: 600 }}>
            Sutra Markdown
          </Typography>
          <Typography variant="titleMedium" color="text.secondary">
            Intelligent document conversion powered by AI
          </Typography>
        </Box>

        {/* Options */}
        <Stack
          direction={{ xs: 'column', sm: 'row' }}
          spacing={2}
          sx={{ justifyContent: 'center', alignItems: 'center' }}
        >
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Conversion Tier</InputLabel>
            <Select
              value={tier}
              label="Conversion Tier"
              onChange={(e) => setTier(e.target.value as any)}
            >
              <MenuItem value="auto">Auto (Recommended)</MenuItem>
              <MenuItem value="tier1">Tier 1 - Rule-Based</MenuItem>
              <MenuItem value="tier2">Tier 2 - Spatial-Aware</MenuItem>
              <MenuItem value="tier3">Tier 3 - LLM-Enhanced</MenuItem>
            </Select>
          </FormControl>

          <FormControlLabel
            control={<Switch checked={useCache} onChange={(e) => setUseCache(e.target.checked)} />}
            label="Use Cache"
          />
        </Stack>

        {/* File Upload */}
        <FileUpload
          onFileSelect={handleFileSelect}
          onFileRemove={handleFileRemove}
          selectedFile={file}
          loading={loading}
          disabled={loading}
        />

        {/* Loading */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <Stack spacing={2} alignItems="center">
              <CircularProgress size={48} />
              <Typography variant="bodyMedium" color="text.secondary">
                Converting document...
              </Typography>
            </Stack>
          </Box>
        )}

        {/* Error */}
        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Result */}
        {result && <ConversionResult result={result} filename={file?.name} />}

        {/* Info */}
        <Box
          sx={{
            p: 3,
            bgcolor: 'surface.container',
            borderRadius: 2,
            textAlign: 'center',
          }}
        >
          <Typography variant="bodySmall" color="text.secondary">
            Supports PDF, DOCX, and PPTX files up to 50MB.
            <br />
            90% of documents are converted with free tier (Tier 1 & 2).
          </Typography>
        </Box>
      </Stack>
    </Container>
  );
};
