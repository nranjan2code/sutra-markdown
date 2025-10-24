/**
 * Main App Component
 * 
 * Root component with theme, routing, and global state
 */

import React, { useState, useMemo } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, CssBaseline, Box, AppBar, Toolbar, Typography, IconButton } from '@mui/material';
import { Brightness4, Brightness7 } from '@mui/icons-material';
import { createAppTheme } from '@/theme';
import { HomePage } from '@/pages';

function App() {
  const [mode, setMode] = useState<'light' | 'dark'>('light');

  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
          {/* App Bar */}
          <AppBar position="static" color="transparent" elevation={0}>
            <Toolbar>
              <Typography variant="titleLarge" component="div" sx={{ flexGrow: 1, fontWeight: 600 }}>
                Sutra
              </Typography>
              <IconButton onClick={toggleTheme} color="inherit">
                {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
              </IconButton>
            </Toolbar>
          </AppBar>

          {/* Routes */}
          <Routes>
            <Route path="/" element={<HomePage />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
