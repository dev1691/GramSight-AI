import React from 'react';
import {
  Card, CardContent, Typography, Box, LinearProgress, Chip,
  Stack, Skeleton,
} from '@mui/material';
import GrassIcon from '@mui/icons-material/Grass';
import ScienceIcon from '@mui/icons-material/Science';

const INDICATORS = [
  { key: 'nitrogen', label: 'Nitrogen (N)', unit: 'kg/ha', optimal: [40, 80] },
  { key: 'phosphorus', label: 'Phosphorus (P)', unit: 'kg/ha', optimal: [30, 60] },
  { key: 'potassium', label: 'Potassium (K)', unit: 'kg/ha', optimal: [50, 80] },
  { key: 'moisture', label: 'Soil Moisture', unit: '%', optimal: [40, 70] },
  { key: 'organic_matter', label: 'Organic Matter', unit: '%', optimal: [2, 5] },
];

function getIndicatorColor(value, optimal) {
  if (value == null) return '#9E9E9E';
  if (value >= optimal[0] && value <= optimal[1]) return '#4CAF50';
  if (value < optimal[0]) return '#FF9800';
  return '#2196F3';
}

function getIndicatorStatus(value, optimal) {
  if (value == null) return 'N/A';
  if (value >= optimal[0] && value <= optimal[1]) return 'Optimal';
  if (value < optimal[0]) return 'Low';
  return 'High';
}

function getProgressValue(value, optimal) {
  if (value == null) return 0;
  const [min, max] = optimal;
  if (value <= min) return Math.min(50, (value / min) * 50);
  if (value >= max) return 100;
  return 50 + ((value - min) / (max - min)) * 50;
}

function getPhInterpretation(ph) {
  if (ph == null) return null;
  if (ph < 5.5) return { label: 'Acidic', color: '#E65100' };
  if (ph <= 6.5) return { label: 'Slightly acidic', color: '#FF9800' };
  if (ph <= 7.5) return { label: 'Neutral', color: '#4CAF50' };
  return { label: 'Alkaline', color: '#2196F3' };
}

function getRecommendations(data) {
  const recs = [];
  INDICATORS.forEach((ind) => {
    const value = data[ind.key];
    if (value == null) return;
    const [min, max] = ind.optimal;
    if (value < min) {
      if (ind.key === 'nitrogen') recs.push('Add nitrogen-rich fertilizer (urea/DAP) to improve soil N.');
      if (ind.key === 'phosphorus') recs.push('Apply phosphorus (DAP/SSP) — levels are below optimal.');
      if (ind.key === 'potassium') recs.push('Consider potash application for better K availability.');
      if (ind.key === 'moisture') recs.push('Increase irrigation — soil moisture is low.');
      if (ind.key === 'organic_matter') recs.push('Add compost or green manure to boost organic matter.');
    } else if (value > max) {
      if (ind.key === 'moisture') recs.push('Reduce irrigation — soil may be waterlogged.');
    }
  });
  const ph = data.ph;
  if (ph != null) {
    if (ph < 5.5) recs.push('Soil is acidic — consider lime application.');
    if (ph > 7.5) recs.push('Soil is alkaline — gypsum or sulfur may help.');
  }
  return recs.slice(0, 3);
}

function hasAnyData(data) {
  if (!data || typeof data !== 'object') return false;
  return INDICATORS.some((ind) => data[ind.key] != null) || data.ph != null;
}

export default function SoilHealthCard({ data, loading }) {
  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ p: 3 }}>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 2.5 }}>
            <Skeleton variant="circular" width={24} height={24} />
            <Skeleton variant="text" width={120} height={28} />
          </Stack>
          {[1, 2, 3, 4, 5].map((i) => (
            <Box key={i} sx={{ mb: 2.5 }}>
              <Skeleton variant="text" width="80%" height={20} />
              <Skeleton variant="rectangular" height={8} sx={{ borderRadius: 4, mt: 0.5 }} />
            </Box>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (!hasAnyData(data)) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <GrassIcon sx={{ color: '#4CAF50' }} />
            <Typography variant="h6">Soil Health</Typography>
          </Box>
          <Box
            sx={{
              py: 4,
              px: 2,
              textAlign: 'center',
              bgcolor: 'rgba(0,0,0,0.02)',
              borderRadius: 2,
              border: '1px dashed rgba(0,0,0,0.12)',
            }}
          >
            <ScienceIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
              No soil data available for this village
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Consider soil testing to get personalized insights and recommendations
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const phInfo = getPhInterpretation(data.ph);
  const recommendations = getRecommendations(data);

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2.5 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <GrassIcon sx={{ color: '#4CAF50' }} />
            <Typography variant="h6">Soil Health</Typography>
          </Box>
          <Stack direction="row" spacing={1} alignItems="center">
            <Chip
              label={`pH ${data.ph != null ? data.ph.toFixed(1) : '--'}`}
              size="small"
              variant="outlined"
              sx={{ fontWeight: 600 }}
            />
            {phInfo && (
              <Chip
                label={phInfo.label}
                size="small"
                sx={{
                  fontSize: '0.7rem',
                  fontWeight: 500,
                  bgcolor: `${phInfo.color}15`,
                  color: phInfo.color,
                }}
              />
            )}
          </Stack>
        </Box>

        {INDICATORS.map((ind) => {
          const value = data[ind.key];
          const color = getIndicatorColor(value, ind.optimal);
          const status = getIndicatorStatus(value, ind.optimal);
          const progress = getProgressValue(value, ind.optimal);
          return (
            <Box key={ind.key} sx={{ mb: 2.5, '&:last-child': { mb: 0 } }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="caption" sx={{ fontWeight: 500, color: 'text.secondary' }}>
                  {ind.label}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="caption" sx={{ fontWeight: 700, color }}>
                    {value != null ? `${value} ${ind.unit}` : '--'}
                  </Typography>
                  {value != null && (
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
                  )}
                </Box>
              </Box>
              <LinearProgress
                variant="determinate"
                value={progress}
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

        {recommendations.length > 0 && (
          <Box sx={{ mt: 2.5, pt: 2, borderTop: '1px solid rgba(0,0,0,0.08)' }}>
            <Typography variant="caption" sx={{ fontWeight: 700, color: 'text.secondary', display: 'block', mb: 1 }}>
              Recommendations
            </Typography>
            <Stack spacing={0.5}>
              {recommendations.map((rec, i) => (
                <Typography key={i} variant="caption" sx={{ fontSize: '0.75rem', color: '#5D4037' }}>
                  • {rec}
                </Typography>
              ))}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
