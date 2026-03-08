import React from 'react';
import { Card, CardContent, Typography, Box, LinearProgress, Chip } from '@mui/material';
import GrassIcon from '@mui/icons-material/Grass';

const DEMO_SOIL = {
  nitrogen: 65,
  phosphorus: 42,
  potassium: 72,
  moisture: 38,
  ph: 6.5,
};

const INDICATORS = [
  { key: 'nitrogen', label: 'Nitrogen (N)', unit: 'kg/ha', optimal: [40, 80] },
  { key: 'phosphorus', label: 'Phosphorus (P)', unit: 'kg/ha', optimal: [30, 60] },
  { key: 'potassium', label: 'Potassium (K)', unit: 'kg/ha', optimal: [50, 80] },
  { key: 'moisture', label: 'Soil Moisture', unit: '%', optimal: [40, 70] },
];

function getIndicatorColor(value, optimal) {
  if (value >= optimal[0] && value <= optimal[1]) return '#4CAF50';
  if (value < optimal[0]) return '#FF9800';
  return '#2196F3';
}

function getIndicatorStatus(value, optimal) {
  if (value >= optimal[0] && value <= optimal[1]) return 'Optimal';
  if (value < optimal[0]) return 'Low';
  return 'High';
}

export default function SoilHealthCard({ data = DEMO_SOIL }) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <GrassIcon sx={{ color: '#4CAF50' }} />
            <Typography variant="h6">Soil Health</Typography>
          </Box>
          <Chip
            label={`pH ${data.ph || '--'}`}
            size="small"
            variant="outlined"
            sx={{ fontWeight: 600 }}
          />
        </Box>

        {INDICATORS.map((ind) => {
          const value = data[ind.key] ?? 0;
          const color = getIndicatorColor(value, ind.optimal);
          const status = getIndicatorStatus(value, ind.optimal);
          return (
            <Box key={ind.key} sx={{ mb: 2.5, '&:last-child': { mb: 0 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="caption" sx={{ fontWeight: 500, color: 'text.secondary' }}>
                  {ind.label}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color }}>
                    {value} {ind.unit}
                  </Typography>
                  <Chip
                    label={status}
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.65rem',
                      fontWeight: 600,
                      bgcolor: `${color}15`,
                      color,
                    }}
                  />
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(value, 100)}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  bgcolor: 'rgba(0,0,0,0.05)',
                  '& .MuiLinearProgress-bar': { bgcolor: color, borderRadius: 4 },
                }}
              />
            </Box>
          );
        })}
      </CardContent>
    </Card>
  );
}
