import { createTheme } from '@mui/material/styles';

export const SIDEBAR_WIDTH = 280;

export const riskColors = {
  low: '#4CAF50',
  moderate: '#FFC107',
  high: '#FF9800',
  critical: '#F44336',
};

export const getRiskColor = (score) => {
  if (score <= 30) return riskColors.low;
  if (score <= 50) return riskColors.moderate;
  if (score <= 70) return riskColors.high;
  return riskColors.critical;
};

export const getRiskLabel = (score) => {
  if (score <= 30) return 'Low';
  if (score <= 50) return 'Moderate';
  if (score <= 70) return 'High';
  return 'Critical';
};

const theme = createTheme({
  palette: {
    primary: { main: '#1B5E20', light: '#4CAF50', dark: '#0D3B12', contrastText: '#fff' },
    secondary: { main: '#FF8F00', light: '#FFB74D', dark: '#E65100', contrastText: '#fff' },
    error: { main: '#D32F2F' },
    warning: { main: '#ED6C02' },
    info: { main: '#0288D1' },
    success: { main: '#2E7D32' },
    background: { default: '#F0F2F5', paper: '#FFFFFF' },
  },
  typography: {
    fontFamily: "'Inter', 'Roboto', 'Helvetica Neue', sans-serif",
    h3: { fontWeight: 800, letterSpacing: '-0.02em' },
    h4: { fontWeight: 700, letterSpacing: '-0.01em' },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    button: { fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06)',
          border: '1px solid rgba(0,0,0,0.05)',
          transition: 'box-shadow 0.2s ease, transform 0.2s ease',
          '&:hover': {
            boxShadow: '0 4px 16px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          textTransform: 'none',
          fontWeight: 600,
          padding: '10px 24px',
        },
        containedPrimary: {
          boxShadow: '0 2px 8px rgba(27, 94, 32, 0.3)',
          '&:hover': { boxShadow: '0 4px 12px rgba(27, 94, 32, 0.4)' },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: { '& .MuiOutlinedInput-root': { borderRadius: 10 } },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 600 } },
    },
  },
});

export default theme;
