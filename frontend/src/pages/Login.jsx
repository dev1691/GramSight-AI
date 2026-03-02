import React, { useState, useContext } from 'react';
import {
  Box, Paper, TextField, Button, Typography, Alert,
  FormControl, InputLabel, Select, MenuItem, Stack, CircularProgress,
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import AuthContext from '../context/AuthContext';
import api from '../services/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('farmer');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, loginDemo } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleDemoLogin = async (role) => {
    await loginDemo(role);
    navigate(role === 'admin' ? '/dashboard/admin' : '/dashboard/farmer');
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/auth/login', { email, password });
      login(res.data.access_token, role);
      navigate(role === 'admin' ? '/dashboard/admin' : '/dashboard/farmer');
    } catch (err) {
      const msg = err?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        background: 'linear-gradient(135deg, #F0F2F5 0%, #E8F5E9 100%)',
      }}
    >
      {/* Left branding panel */}
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          width: '45%',
          background: 'linear-gradient(165deg, #0D3B12 0%, #1B5E20 50%, #2E7D32 100%)',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          p: 6,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute', top: -80, right: -80,
            width: 300, height: 300, borderRadius: '50%',
            background: 'rgba(255,255,255,0.04)',
          }}
        />
        <Box
          sx={{
            position: 'absolute', bottom: -100, left: -50,
            width: 250, height: 250, borderRadius: '50%',
            background: 'rgba(255,255,255,0.03)',
          }}
        />
        <Box sx={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
          <Box
            sx={{
              width: 80, height: 80, borderRadius: 4, mb: 3, mx: 'auto',
              background: 'rgba(255,255,255,0.1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              border: '2px solid rgba(255,255,255,0.15)',
            }}
          >
            <AgricultureIcon sx={{ fontSize: 40, color: '#fff' }} />
          </Box>
          <Typography variant="h4" sx={{ color: '#fff', fontWeight: 800, mb: 2 }}>
            GramSight AI
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.75)', maxWidth: 320, lineHeight: 1.7 }}>
            Smart agricultural risk intelligence platform. Monitor weather, markets,
            and soil health — all in one place.
          </Typography>
        </Box>
      </Box>

      {/* Right form panel */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          p: { xs: 3, md: 6 },
        }}
      >
        <Paper
          elevation={0}
          sx={{
            p: { xs: 3, md: 5 },
            width: '100%',
            maxWidth: 440,
            borderRadius: 4,
            border: '1px solid rgba(0,0,0,0.08)',
          }}
        >
          <Box sx={{ display: { xs: 'flex', md: 'none' }, alignItems: 'center', gap: 1, mb: 3 }}>
            <AgricultureIcon sx={{ color: '#1B5E20' }} />
            <Typography variant="h6" sx={{ fontWeight: 800, color: '#1B2A3D' }}>
              GramSight <span style={{ color: '#4CAF50' }}>AI</span>
            </Typography>
          </Box>

          <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5, color: '#1B2A3D' }}>
            Welcome back
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Sign in to access your dashboard
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}

          <form onSubmit={onSubmit}>
            <TextField
              label="Email"
              type="email"
              fullWidth
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              autoFocus
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />

            <FormControl fullWidth margin="normal" size="medium">
              <InputLabel>Sign in as</InputLabel>
              <Select
                value={role}
                label="Sign in as"
                onChange={(e) => setRole(e.target.value)}
              >
                <MenuItem value="farmer">Farmer</MenuItem>
                <MenuItem value="admin">Government / NGO Admin</MenuItem>
              </Select>
            </FormControl>

            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              size="large"
              disabled={loading}
              sx={{ mt: 3, py: 1.5 }}
            >
              {loading ? <CircularProgress size={22} color="inherit" /> : 'Sign In'}
            </Button>

            <Stack direction="row" spacing={1.5} sx={{ mt: 2 }}>
              <Button
                type="button"
                variant="outlined"
                fullWidth
                size="medium"
                onClick={() => handleDemoLogin('farmer')}
                sx={{ py: 1.2, borderColor: 'primary.main', color: 'primary.main' }}
              >
                View Farmer Demo
              </Button>
              <Button
                type="button"
                variant="outlined"
                fullWidth
                size="medium"
                onClick={() => handleDemoLogin('admin')}
                sx={{ py: 1.2, borderColor: 'secondary.main', color: 'secondary.main' }}
              >
                View Admin Demo
              </Button>
            </Stack>
          </form>

          <Stack direction="row" justifyContent="center" spacing={0.5} sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account?
            </Typography>
            <Typography
              component={RouterLink}
              to="/register"
              variant="body2"
              sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none' }}
            >
              Create one
            </Typography>
          </Stack>
        </Paper>
      </Box>
    </Box>
  );
}
