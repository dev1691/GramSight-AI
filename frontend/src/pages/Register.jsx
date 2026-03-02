import React, { useState, useContext } from 'react';
import {
  Box, Paper, TextField, Button, Typography, Alert,
  FormControl, InputLabel, Select, MenuItem, Stack, CircularProgress,
} from '@mui/material';
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import AuthContext from '../context/AuthContext';
import api from '../services/api';

export default function Register() {
  const [searchParams] = useSearchParams();
  const defaultRole = searchParams.get('role') || 'farmer';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState(defaultRole);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.post('/auth/register', { email, password, role });
      login(res.data.access_token, role);
      navigate(role === 'admin' ? '/dashboard/admin' : '/dashboard/farmer');
    } catch (err) {
      const msg = err?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Registration failed. Email may already be in use.');
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
            Join GramSight AI
          </Typography>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.75)', maxWidth: 320, lineHeight: 1.7 }}>
            Create your account to access real-time agricultural intelligence,
            risk scores, weather forecasts, and AI-powered advisories.
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
            Create account
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Get started with your agricultural dashboard
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
              autoComplete="new-password"
              helperText="Minimum 6 characters"
            />
            <TextField
              label="Confirm Password"
              type="password"
              fullWidth
              margin="normal"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />

            <FormControl fullWidth margin="normal" size="medium">
              <InputLabel>I am a</InputLabel>
              <Select value={role} label="I am a" onChange={(e) => setRole(e.target.value)}>
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
              {loading ? <CircularProgress size={22} color="inherit" /> : 'Create Account'}
            </Button>
          </form>

          <Stack direction="row" justifyContent="center" spacing={0.5} sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?
            </Typography>
            <Typography
              component={RouterLink}
              to="/login"
              variant="body2"
              sx={{ color: 'primary.main', fontWeight: 600, textDecoration: 'none' }}
            >
              Sign in
            </Typography>
          </Stack>
        </Paper>
      </Box>
    </Box>
  );
}
