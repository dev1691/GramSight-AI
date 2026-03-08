import React, { useContext } from 'react';
import { Box, Typography, Button, Container, Grid, Card, CardContent, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import SpeedIcon from '@mui/icons-material/Speed';
import WbSunnyIcon from '@mui/icons-material/WbSunny';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PsychologyIcon from '@mui/icons-material/Psychology';
import SecurityIcon from '@mui/icons-material/Security';
import GroupsIcon from '@mui/icons-material/Groups';

const FEATURES = [
  {
    icon: <SpeedIcon sx={{ fontSize: 32 }} />,
    title: 'Risk Scoring Engine',
    description: 'Multi-factor risk assessment combining weather, soil, and market data into actionable scores.',
    color: '#FF8F00',
  },
  {
    icon: <WbSunnyIcon sx={{ fontSize: 32 }} />,
    title: 'Weather Intelligence',
    description: '5-day weather forecasts with temperature, rainfall, and humidity trend analysis.',
    color: '#36A2EB',
  },
  {
    icon: <TrendingUpIcon sx={{ fontSize: 32 }} />,
    title: 'Market Analytics',
    description: 'Real-time crop price tracking with volatility indicators and trend predictions.',
    color: '#4CAF50',
  },
  {
    icon: <PsychologyIcon sx={{ fontSize: 32 }} />,
    title: 'AI Advisory',
    description: 'LLM-powered recommendations tailored to your village conditions and crop needs.',
    color: '#9C27B0',
  },
  {
    icon: <SecurityIcon sx={{ fontSize: 32 }} />,
    title: 'Soil Health Monitoring',
    description: 'Track nitrogen, phosphorus, potassium levels and soil moisture in real-time.',
    color: '#795548',
  },
  {
    icon: <GroupsIcon sx={{ fontSize: 32 }} />,
    title: 'Multi-Role Dashboards',
    description: 'Purpose-built views for farmers and government administrators with role-based access.',
    color: '#E91E63',
  },
];

export default function Landing() {
  const navigate = useNavigate();
  const { loginDemo } = useContext(AuthContext);

  const handleDemo = (role) => {
    loginDemo(role);
    navigate(role === 'admin' ? '/dashboard/admin' : '/dashboard/farmer');
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#FAFAF8' }}>
      {/* Navbar */}
      <Box
        sx={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
          bgcolor: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(0,0,0,0.06)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ display: 'flex', alignItems: 'center', py: 1.5 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
              <Box
                sx={{
                  width: 36, height: 36, borderRadius: 2,
                  background: 'linear-gradient(135deg, #4CAF50 0%, #1B5E20 100%)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}
              >
                <AgricultureIcon sx={{ fontSize: 20, color: '#fff' }} />
              </Box>
              <Typography variant="h6" sx={{ fontWeight: 800, color: '#1B2A3D' }}>
                GramSight <span style={{ color: '#4CAF50' }}>AI</span>
              </Typography>
            </Box>
            <Stack direction="row" spacing={1.5} flexWrap="wrap">
              <Button onClick={() => handleDemo('farmer')} variant="outlined" sx={{ borderColor: '#4CAF50', color: '#1B5E20' }}>
                Farmer Demo
              </Button>
              <Button onClick={() => handleDemo('admin')} variant="outlined" sx={{ borderColor: '#FF8F00', color: '#E65100' }}>
                Admin Demo
              </Button>
              <Button onClick={() => navigate('/login')} variant="text" sx={{ color: '#1B2A3D' }}>
                Sign In
              </Button>
              <Button onClick={() => navigate('/register')} variant="contained" color="primary">
                Get Started
              </Button>
            </Stack>
          </Box>
        </Container>
      </Box>

      {/* Hero */}
      <Box
        sx={{
          pt: { xs: 14, md: 18 },
          pb: { xs: 8, md: 12 },
          background: 'linear-gradient(165deg, #0D3B12 0%, #1B5E20 35%, #2E7D32 70%, #4CAF50 100%)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute', top: -100, right: -100,
            width: 500, height: 500, borderRadius: '50%',
            background: 'rgba(255,255,255,0.03)',
          }}
        />
        <Box
          sx={{
            position: 'absolute', bottom: -150, left: -100,
            width: 400, height: 400, borderRadius: '50%',
            background: 'rgba(255,255,255,0.03)',
          }}
        />

        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={7}>
              <Typography
                variant="overline"
                sx={{ color: 'rgba(255,255,255,0.7)', letterSpacing: 3, mb: 2, display: 'block' }}
              >
                SMART AGRICULTURE PLATFORM
              </Typography>
              <Typography
                variant="h3"
                sx={{
                  color: '#fff', fontWeight: 800, lineHeight: 1.15,
                  fontSize: { xs: '2rem', md: '3rem' },
                  mb: 3,
                }}
              >
                Village-Level Risk Intelligence for{' '}
                <span style={{ color: '#FFD54F' }}>Sustainable Agriculture</span>
              </Typography>
              <Typography
                variant="h6"
                sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 400, lineHeight: 1.6, mb: 4, maxWidth: 560 }}
              >
                Empowering farmers with real-time weather insights, market analytics,
                soil health monitoring, and AI-powered advisories to make smarter
                agricultural decisions.
              </Typography>
              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button
                  onClick={() => navigate('/register')}
                  variant="contained"
                  size="large"
                  sx={{
                    bgcolor: '#fff', color: '#1B5E20', fontWeight: 700,
                    px: 4, py: 1.5, fontSize: '1rem',
                    '&:hover': { bgcolor: '#F5F5F5', boxShadow: '0 8px 24px rgba(0,0,0,0.2)' },
                  }}
                >
                  Start as Farmer
                </Button>
                <Button
                  onClick={() => navigate('/register?role=admin')}
                  variant="outlined"
                  size="large"
                  sx={{
                    borderColor: 'rgba(255,255,255,0.5)', color: '#fff',
                    px: 4, py: 1.5, fontSize: '1rem',
                    '&:hover': { borderColor: '#fff', bgcolor: 'rgba(255,255,255,0.08)' },
                  }}
                >
                  Admin Dashboard
                </Button>
              </Stack>
            </Grid>
            <Grid item xs={12} md={5} sx={{ display: { xs: 'none', md: 'flex' }, justifyContent: 'center' }}>
              <Box
                sx={{
                  width: 320, height: 320, borderRadius: '50%',
                  background: 'rgba(255,255,255,0.06)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  border: '2px solid rgba(255,255,255,0.1)',
                }}
              >
                <Box
                  sx={{
                    width: 240, height: 240, borderRadius: '50%',
                    background: 'rgba(255,255,255,0.06)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    border: '2px solid rgba(255,255,255,0.08)',
                  }}
                >
                  <AgricultureIcon sx={{ fontSize: 100, color: 'rgba(255,255,255,0.6)' }} />
                </Box>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features */}
      <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h4" sx={{ fontWeight: 800, color: '#1B2A3D', mb: 1.5 }}>
            Comprehensive Agricultural Intelligence
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Six integrated modules providing end-to-end risk assessment and actionable insights
            for rural agriculture.
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {FEATURES.map((f) => (
            <Grid item xs={12} sm={6} md={4} key={f.title}>
              <Card
                sx={{
                  height: '100%',
                  transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                  '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 12px 32px rgba(0,0,0,0.1)' },
                }}
              >
                <CardContent sx={{ p: 3.5 }}>
                  <Box
                    sx={{
                      width: 56, height: 56, borderRadius: 3, mb: 2.5,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      bgcolor: `${f.color}12`, color: f.color,
                    }}
                  >
                    {f.icon}
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, mb: 1, color: '#1B2A3D' }}>
                    {f.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                    {f.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Stats Bar */}
      <Box sx={{ bgcolor: '#1B2A3D', py: 6 }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} justifyContent="center">
            {[
              { value: '2', label: 'User Personas' },
              { value: '6', label: 'Core Modules' },
              { value: '12+', label: 'API Endpoints' },
              { value: '5', label: 'Data Sources' },
            ].map((stat) => (
              <Grid item xs={6} md={3} key={stat.label}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h3" sx={{ color: '#4CAF50', fontWeight: 800 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.6)', mt: 0.5 }}>
                    {stat.label}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Footer */}
      <Box sx={{ py: 4, textAlign: 'center', borderTop: '1px solid rgba(0,0,0,0.06)' }}>
        <Typography variant="body2" color="text.secondary">
          GramSight AI — Built for sustainable agriculture
        </Typography>
      </Box>
    </Box>
  );
}
