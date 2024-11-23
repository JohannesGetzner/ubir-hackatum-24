import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#2196f3', // Light blue
      light: '#64b5f6',
      dark: '#1976d2',
    },
    secondary: {
      main: '#e3f2fd', // Very light blue
      light: '#ffffff',
      dark: '#b1bfca',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
    text: {
      primary: '#1a237e',
      secondary: '#455a64',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Inter", sans-serif',
    h6: {
      fontWeight: 500,
      letterSpacing: 0.5,
    },
    subtitle1: {
      letterSpacing: 0.3,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#ffffff',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#ffffff',
          borderRight: 'none',
          boxShadow: '2px 0 10px rgba(0, 0, 0, 0.05)',
        },
      },
    },
  },
});
