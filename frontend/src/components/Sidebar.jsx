import React, { useContext } from 'react';
import {
  Drawer, Box, Typography, List, ListItemButton,
  ListItemIcon, ListItemText, Divider, Avatar, IconButton,
} from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import AgricultureIcon from '@mui/icons-material/Agriculture';
import LogoutIcon from '@mui/icons-material/Logout';
import AuthContext from '../context/AuthContext';

const FARMER_NAV = [
  { label: 'Farmer Dashboard', icon: <DashboardIcon />, path: '/dashboard/farmer' },
];

const ADMIN_NAV = [
  { label: 'Admin Dashboard', icon: <AdminPanelSettingsIcon />, path: '/dashboard/admin' },
];

export default function Sidebar({ width, mobileOpen, onClose, isMobile }) {
  const { user, role, logout } = useContext(AuthContext);
  const location = useLocation();
  const navigate = useNavigate();

  const navItems = role === 'admin'
    ? [...ADMIN_NAV, ...FARMER_NAV]
    : [...FARMER_NAV, ...ADMIN_NAV];

  const content = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(180deg, #1B2A3D 0%, #0F1724 100%)',
        color: '#fff',
      }}
    >
      <Box sx={{ p: 3, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 40, height: 40, borderRadius: 2,
            background: 'linear-gradient(135deg, #4CAF50 0%, #1B5E20 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <AgricultureIcon sx={{ fontSize: 24, color: '#fff' }} />
        </Box>
        <Box>
          <Typography
            variant="h6"
            sx={{ fontWeight: 800, lineHeight: 1.1, color: '#fff', fontSize: '1.1rem' }}
          >
            GramSight
          </Typography>
          <Typography
            variant="caption"
            sx={{ color: '#4CAF50', fontWeight: 700, letterSpacing: 3, fontSize: '0.65rem' }}
          >
            AI PLATFORM
          </Typography>
        </Box>
      </Box>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)', mx: 2 }} />

      <Typography
        variant="overline"
        sx={{ px: 3, pt: 2.5, pb: 1, color: 'rgba(255,255,255,0.35)', fontSize: '0.65rem', letterSpacing: 1.5 }}
      >
        Navigation
      </Typography>

      <List sx={{ flex: 1, px: 2 }}>
        {navItems.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.path}
              onClick={() => { navigate(item.path); if (isMobile) onClose(); }}
              sx={{
                borderRadius: 2, mb: 0.5, px: 2, py: 1.2,
                bgcolor: active ? 'rgba(76, 175, 80, 0.15)' : 'transparent',
                color: active ? '#4CAF50' : 'rgba(255,255,255,0.65)',
                '&:hover': { bgcolor: 'rgba(255,255,255,0.06)', color: '#fff' },
                transition: 'all 0.15s ease',
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.label}
                primaryTypographyProps={{ fontSize: 14, fontWeight: active ? 600 : 400 }}
              />
              {active && (
                <Box sx={{ width: 4, height: 24, borderRadius: 2, bgcolor: '#4CAF50' }} />
              )}
            </ListItemButton>
          );
        })}
      </List>

      <Divider sx={{ borderColor: 'rgba(255,255,255,0.06)', mx: 2 }} />

      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar
          sx={{
            width: 36, height: 36, fontSize: 14, fontWeight: 700,
            background: 'linear-gradient(135deg, #4CAF50 0%, #1B5E20 100%)',
          }}
        >
          {user?.email?.[0]?.toUpperCase() || 'U'}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography
            variant="body2"
            sx={{
              color: '#fff', fontWeight: 500, fontSize: 13,
              overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
            }}
          >
            {user?.email || 'User'}
          </Typography>
          <Typography
            variant="caption"
            sx={{ color: 'rgba(255,255,255,0.4)', textTransform: 'capitalize', fontSize: 11 }}
          >
            {role || 'farmer'}
          </Typography>
        </Box>
        <IconButton
          onClick={logout}
          size="small"
          sx={{ color: 'rgba(255,255,255,0.4)', '&:hover': { color: '#F44336', bgcolor: 'rgba(244,67,54,0.1)' } }}
        >
          <LogoutIcon fontSize="small" />
        </IconButton>
      </Box>
    </Box>
  );

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{ '& .MuiDrawer-paper': { width, border: 'none' } }}
      >
        {content}
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      open
      sx={{ '& .MuiDrawer-paper': { width, border: 'none', position: 'fixed' } }}
    >
      {content}
    </Drawer>
  );
}
