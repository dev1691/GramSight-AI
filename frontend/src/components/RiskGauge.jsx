import React from 'react';
import { Card, CardContent, Box, Typography, Chip } from '@mui/material';
import { getRiskColor, getRiskLabel } from '../theme/theme';

export default function RiskGauge({ score = 0, size = 220, lastUpdated }) {
  const s = Math.min(100, Math.max(0, Math.round(score)));
  const color = getRiskColor(s);
  const label = getRiskLabel(s);

  const radius = (size - 24) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = Math.PI * radius;
  const progress = (s / 100) * circumference;

  const arcPath = `M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 3, '&:last-child': { pb: 3 } }}>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 1, fontWeight: 600 }}>
          Village Risk Score
        </Typography>

        <Box sx={{ position: 'relative', width: size, height: size / 2 + 30 }}>
          <svg width={size} height={size / 2 + 10} viewBox={`0 0 ${size} ${size / 2 + 10}`}>
            <path
              d={arcPath}
              fill="none"
              stroke="#E8E8E8"
              strokeWidth="14"
              strokeLinecap="round"
            />
            <path
              d={arcPath}
              fill="none"
              stroke={color}
              strokeWidth="14"
              strokeLinecap="round"
              strokeDasharray={`${progress} ${circumference}`}
              style={{ transition: 'stroke-dasharray 0.8s ease-out, stroke 0.4s ease' }}
            />
            <text x={12} y={cy + 20} fontSize="11" fill="#999" textAnchor="start">0</text>
            <text x={size - 12} y={cy + 20} fontSize="11" fill="#999" textAnchor="end">100</text>
          </svg>

          <Box
            sx={{
              position: 'absolute',
              bottom: 12,
              left: '50%',
              transform: 'translateX(-50%)',
              textAlign: 'center',
            }}
          >
            <Typography variant="h3" sx={{ fontWeight: 800, color, lineHeight: 1, fontSize: '2.8rem' }}>
              {s}
            </Typography>
          </Box>
        </Box>

        <Chip
          label={label}
          sx={{
            mt: 1,
            px: 1,
            bgcolor: `${color}18`,
            color,
            fontWeight: 700,
            fontSize: '0.85rem',
            height: 32,
          }}
        />

        {lastUpdated && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Updated {lastUpdated}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
