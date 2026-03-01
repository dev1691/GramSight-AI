import React, { useContext } from 'react';
import { AppBar, Toolbar, Typography, IconButton, Chip, Box } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import { useLocation } from 'react-router-dom';
import AuthContext from '../context/AuthContext';

const PAGE_TITLES = {
  '/dashboard/farmer': 'Farmer Dashboard',
  '/dashboard/admin': 'Admin Dashboard',
};

export default function Topbar({ onMenuClick, isMobile }) {
  const { role } = useContext(AuthContext);
  const location = useLocation();
  const pageTitle = PAGE_TITLES[location.pathname] || 'Dashboard';

  return (
    <AppBar
      position="sticky"
      color="inherit"
      elevation={0}
      sx={{
        bgcolor: 'rgba(255,255,255,0.9)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid',
        borderColor: 'divider',
        zIndex: (t) => t.zIndex.appBar,
      }}
    >
      <Toolbar sx={{ gap: 1.5 }}>
        {isMobile && (
          <IconButton onClick={onMenuClick} edge="start" size="large">
            <MenuIcon />
          </IconButton>
        )}
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, color: 'text.primary', fontSize: '1.1rem' }}>
            {pageTitle}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Real-time agricultural intelligence
          </Typography>
        </Box>
        <Chip
          label={role === 'admin' ? 'Admin' : 'Farmer'}
          size="small"
          sx={{
            bgcolor: role === 'admin' ? 'rgba(255,143,0,0.1)' : 'rgba(76,175,80,0.1)',
            color: role === 'admin' ? 'secondary.dark' : 'primary.main',
            fontWeight: 600,
            border: '1px solid',
            borderColor: role === 'admin' ? 'rgba(255,143,0,0.3)' : 'rgba(76,175,80,0.3)',
          }}
        />
        <IconButton size="small" sx={{ color: 'text.secondary' }}>
          <NotificationsNoneIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
}
