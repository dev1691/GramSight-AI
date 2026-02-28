import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    primary: { main: '#0b6b2f' },
    secondary: { main: '#7a4f33' },
    background: { default: '#f7f7f5', paper: '#ffffff' }
  },
  typography: {
    fontFamily: ['Inter', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'].join(',')
  }
})

export default theme
