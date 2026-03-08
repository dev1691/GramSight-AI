import React, { useState } from 'react';
import { Box, useMediaQuery, useTheme } from '@mui/material';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';
import { SIDEBAR_WIDTH } from '../theme/theme';

export default function DashboardLayout() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      <Sidebar
        width={SIDEBAR_WIDTH}
        mobileOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        isMobile={isMobile}
      />
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          ml: isMobile ? 0 : `${SIDEBAR_WIDTH}px`,
          minHeight: '100vh',
        }}
      >
        <Topbar onMenuClick={() => setMobileOpen(true)} isMobile={isMobile} />
        <Box
          component="main"
          sx={{ flex: 1, p: { xs: 2, sm: 2.5, md: 3 }, overflow: 'auto' }}
        >
          <Outlet />
        </Box>
      </Box>
    </Box>
  );
}
