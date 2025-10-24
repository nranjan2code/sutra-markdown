/**
 * Material Design 3 Theme Configuration
 * 
 * Custom M3 theme with minimal, modern aesthetics
 * Follows Material You design principles
 */

import { createTheme } from '@mui/material/styles';

// M3 Color Palette - Minimal & Professional
const palette = {
  light: {
    primary: {
      main: '#6750A4',
      light: '#9A82DB',
      dark: '#4F378B',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#625B71',
      light: '#8E8799',
      dark: '#4A4458',
      contrastText: '#FFFFFF',
    },
    tertiary: {
      main: '#7D5260',
      light: '#A67C89',
      dark: '#633B48',
      contrastText: '#FFFFFF',
    },
    error: {
      main: '#BA1A1A',
      light: '#DE3730',
      dark: '#93000A',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#006D3C',
      light: '#4C9F70',
      dark: '#004D29',
      contrastText: '#FFFFFF',
    },
    warning: {
      main: '#7D5700',
      light: '#B07F00',
      dark: '#5D4000',
      contrastText: '#FFFFFF',
    },
    background: {
      default: '#FEF7FF',
      paper: '#FFFFFF',
    },
    surface: {
      main: '#FEF7FF',
      variant: '#E7E0EC',
      dim: '#DED8E1',
      bright: '#FEF7FF',
      container: '#F3EDF7',
      containerHigh: '#ECE6F0',
      containerHighest: '#E6E0E9',
    },
    text: {
      primary: '#1D1B20',
      secondary: '#49454F',
      disabled: '#C4C4C4',
    },
    divider: '#CAC4D0',
  },
  dark: {
    primary: {
      main: '#D0BCFF',
      light: '#EADDFF',
      dark: '#9A82DB',
      contrastText: '#381E72',
    },
    secondary: {
      main: '#CCC2DC',
      light: '#E8DEF8',
      dark: '#958DA5',
      contrastText: '#332D41',
    },
    tertiary: {
      main: '#EFB8C8',
      light: '#FFD8E4',
      dark: '#B58392',
      contrastText: '#492532',
    },
    error: {
      main: '#FFB4AB',
      light: '#FFDAD6',
      dark: '#FF897D',
      contrastText: '#690005',
    },
    success: {
      main: '#6FDD8B',
      light: '#C4EED0',
      dark: '#4CB263',
      contrastText: '#00390F',
    },
    warning: {
      main: '#EFBD48',
      light: '#FFE8B0',
      dark: '#C79500',
      contrastText: '#3F2E00',
    },
    background: {
      default: '#141218',
      paper: '#1D1B20',
    },
    surface: {
      main: '#141218',
      variant: '#49454F',
      dim: '#141218',
      bright: '#3B383E',
      container: '#211F26',
      containerHigh: '#2B2930',
      containerHighest: '#36343B',
    },
    text: {
      primary: '#E6E0E9',
      secondary: '#CAC4D0',
      disabled: '#625B71',
    },
    divider: '#49454F',
  },
};

// M3 Typography - Clean & Readable
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  
  // Display
  displayLarge: {
    fontSize: '3.5625rem',
    fontWeight: 400,
    lineHeight: 1.12,
    letterSpacing: '-0.015625rem',
  },
  displayMedium: {
    fontSize: '2.8125rem',
    fontWeight: 400,
    lineHeight: 1.16,
    letterSpacing: 0,
  },
  displaySmall: {
    fontSize: '2.25rem',
    fontWeight: 400,
    lineHeight: 1.22,
    letterSpacing: 0,
  },
  
  // Headline
  headlineLarge: {
    fontSize: '2rem',
    fontWeight: 400,
    lineHeight: 1.25,
    letterSpacing: 0,
  },
  headlineMedium: {
    fontSize: '1.75rem',
    fontWeight: 400,
    lineHeight: 1.29,
    letterSpacing: 0,
  },
  headlineSmall: {
    fontSize: '1.5rem',
    fontWeight: 400,
    lineHeight: 1.33,
    letterSpacing: 0,
  },
  
  // Title
  titleLarge: {
    fontSize: '1.375rem',
    fontWeight: 500,
    lineHeight: 1.27,
    letterSpacing: 0,
  },
  titleMedium: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
    letterSpacing: '0.009375rem',
  },
  titleSmall: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.43,
    letterSpacing: '0.00625rem',
  },
  
  // Body
  bodyLarge: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.5,
    letterSpacing: '0.03125rem',
  },
  bodyMedium: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.43,
    letterSpacing: '0.015625rem',
  },
  bodySmall: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.33,
    letterSpacing: '0.025rem',
  },
  
  // Label
  labelLarge: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.43,
    letterSpacing: '0.00625rem',
  },
  labelMedium: {
    fontSize: '0.75rem',
    fontWeight: 500,
    lineHeight: 1.33,
    letterSpacing: '0.03125rem',
  },
  labelSmall: {
    fontSize: '0.6875rem',
    fontWeight: 500,
    lineHeight: 1.45,
    letterSpacing: '0.03125rem',
  },
};

// M3 Shape - Rounded corners
const shape = {
  borderRadius: 12,
};

// M3 Elevation & Shadows
const shadows = (mode: 'light' | 'dark') => {
  const shadowColor = mode === 'light' ? '0, 0, 0' : '0, 0, 0';
  
  return [
    'none',
    `0px 1px 2px rgba(${shadowColor}, 0.3), 0px 1px 3px rgba(${shadowColor}, 0.15)`,
    `0px 1px 2px rgba(${shadowColor}, 0.3), 0px 2px 6px rgba(${shadowColor}, 0.15)`,
    `0px 4px 8px rgba(${shadowColor}, 0.15), 0px 1px 3px rgba(${shadowColor}, 0.3)`,
    `0px 6px 10px rgba(${shadowColor}, 0.15), 0px 1px 18px rgba(${shadowColor}, 0.12)`,
    `0px 8px 12px rgba(${shadowColor}, 0.15), 0px 4px 4px rgba(${shadowColor}, 0.3)`,
  ];
};

// Component customizations
const getComponents = (mode: 'light' | 'dark') => ({
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 20,
        textTransform: 'none' as const,
        fontWeight: 500,
        padding: '10px 24px',
      },
      contained: {
        boxShadow: 'none',
        '&:hover': {
          boxShadow: shadows(mode)[2],
        },
      },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        boxShadow: shadows(mode)[1],
      },
    },
  },
  MuiPaper: {
    styleOverrides: {
      rounded: {
        borderRadius: 16,
      },
    },
  },
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 8,
      },
    },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 12,
        },
      },
    },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: 'none',
        borderBottom: `1px solid ${mode === 'light' ? palette.light.divider : palette.dark.divider}`,
      },
    },
  },
});

export const createAppTheme = (mode: 'light' | 'dark') => {
  const paletteMode = mode === 'light' ? palette.light : palette.dark;
  
  return createTheme({
    palette: {
      mode,
      ...paletteMode,
    },
    typography: typography as any,
    shape,
    shadows: shadows(mode) as any,
    components: getComponents(mode),
  });
};


