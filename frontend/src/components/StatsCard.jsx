import React from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

export default function StatsCard({ title, value, subtitle, icon, color = '#1B5E20', trend, trendLabel }) {
  const isPositive = trend > 0;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5, fontWeight: 500, fontSize: 13 }}>
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 800, color }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                {subtitle}
              </Typography>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                width: 48, height: 48, borderRadius: 3,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                bgcolor: `${color}15`,
                color,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
        {trend !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 2 }}>
            {isPositive
              ? <TrendingUpIcon sx={{ fontSize: 16, color: 'success.main' }} />
              : <TrendingDownIcon sx={{ fontSize: 16, color: 'error.main' }} />
            }
            <Typography
              variant="caption"
              sx={{ color: isPositive ? 'success.main' : 'error.main', fontWeight: 700 }}
            >
              {isPositive ? '+' : ''}{trend}%
            </Typography>
            {trendLabel && (
              <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                {trendLabel}
              </Typography>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
