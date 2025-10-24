/**
 * FileUpload Component
 * 
 * Beautiful drag-and-drop file upload with M3 design
 */

import React, { useCallback, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Stack,
  IconButton,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  InsertDriveFile as FileIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import type { FileUploadProps } from '../../types/components';

export const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onFileRemove,
  accept = '.pdf,.docx,.pptx,.doc,.ppt',
  maxSize = 50 * 1024 * 1024, // 50MB
  disabled = false,
  loading = false,
  progress,
  selectedFile,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const validateFile = (file: File): string | null => {
    if (maxSize && file.size > maxSize) {
      return `File size exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`;
    }
    
    if (accept) {
      const extensions = accept.split(',').map(ext => ext.trim());
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!extensions.includes(fileExt)) {
        return `File type not supported. Accepted: ${accept}`;
      }
    }
    
    return null;
  };

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      setError(null);

      if (disabled || loading) return;

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        const validationError = validateFile(file);
        
        if (validationError) {
          setError(validationError);
        } else {
          onFileSelect(file);
        }
      }
    },
    [disabled, loading, onFileSelect, maxSize, accept]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    setError(null);

    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validationError = validateFile(file);
      
      if (validationError) {
        setError(validationError);
      } else {
        onFileSelect(file);
      }
    }
  };

  const handleRemove = () => {
    setError(null);
    if (onFileRemove) {
      onFileRemove();
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1024 / 1024).toFixed(1) + ' MB';
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper
        elevation={0}
        sx={{
          position: 'relative',
          p: 4,
          border: '2px dashed',
          borderColor: dragActive
            ? 'primary.main'
            : error
            ? 'error.main'
            : 'divider',
          borderRadius: 3,
          bgcolor: dragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.3s ease',
          cursor: disabled || loading ? 'not-allowed' : 'pointer',
          opacity: disabled || loading ? 0.6 : 1,
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && !loading && document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept={accept}
          onChange={handleChange}
          disabled={disabled || loading}
          style={{ display: 'none' }}
        />

        {selectedFile ? (
          <Stack spacing={2} alignItems="center">
            <FileIcon sx={{ fontSize: 48, color: 'primary.main' }} />
            <Box sx={{ textAlign: 'center', width: '100%' }}>
              <Typography variant="titleMedium" gutterBottom>
                {selectedFile.name}
              </Typography>
              <Typography variant="bodySmall" color="text.secondary">
                {formatFileSize(selectedFile.size)}
              </Typography>
            </Box>
            {!loading && (
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove();
                }}
                sx={{ position: 'absolute', top: 8, right: 8 }}
              >
                <CloseIcon />
              </IconButton>
            )}
            {loading && progress !== undefined && (
              <Box sx={{ width: '100%', mt: 2 }}>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="bodySmall" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
                  {Math.round(progress)}% Complete
                </Typography>
              </Box>
            )}
          </Stack>
        ) : (
          <Stack spacing={2} alignItems="center">
            <UploadIcon sx={{ fontSize: 64, color: 'primary.main', opacity: 0.6 }} />
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="titleLarge" gutterBottom>
                Drop your file here
              </Typography>
              <Typography variant="bodyMedium" color="text.secondary" gutterBottom>
                or click to browse
              </Typography>
              <Typography variant="bodySmall" color="text.secondary">
                Supports: PDF, DOCX, PPTX (max {Math.round(maxSize / 1024 / 1024)}MB)
              </Typography>
            </Box>
            <Button
              variant="contained"
              startIcon={<UploadIcon />}
              disabled={disabled || loading}
              onClick={(e) => e.stopPropagation()}
            >
              Choose File
            </Button>
          </Stack>
        )}

        {error && (
          <Typography
            variant="bodySmall"
            color="error"
            sx={{ mt: 2, textAlign: 'center' }}
          >
            {error}
          </Typography>
        )}
      </Paper>
    </Box>
  );
};
