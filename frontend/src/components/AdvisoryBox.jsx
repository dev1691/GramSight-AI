import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Skeleton, Divider } from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import LightbulbIcon from '@mui/icons-material/Lightbulb';

const DEMO_ADVISORY = [
  'Increase watering frequency — rising temperatures and low rainfall forecast for the next 3 days.',
  'Rice prices trending upward (+2.4%) — consider holding current stock for 1-2 more weeks before selling.',
  'Apply organic mulch to retain soil moisture. Current nitrogen levels are adequate, but phosphorus is low.',
  'Monitor weather alerts closely — dry spell expected. Plan irrigation schedules accordingly.',
];

export default function AdvisoryBox({ items = DEMO_ADVISORY, loading = false }) {
  if (loading) {
    return (
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Skeleton variant="text" width={200} height={32} />
          <Skeleton variant="rectangular" height={40} sx={{ mt: 2, borderRadius: 2 }} />
          <Skeleton variant="rectangular" height={40} sx={{ mt: 1, borderRadius: 2 }} />
          <Skeleton variant="rectangular" height={40} sx={{ mt: 1, borderRadius: 2 }} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      sx={{
        height: '100%',
        border: '1px solid',
        borderColor: 'rgba(76, 175, 80, 0.2)',
        background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.02) 0%, rgba(255,255,255,1) 100%)',
      }}
    >
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <PsychologyIcon sx={{ color: 'primary.main' }} />
            <Typography variant="h6">AI Advisory</Typography>
          </Box>
          <Chip
            icon={<AutoAwesomeIcon sx={{ fontSize: '14px !important' }} />}
            label="AI Powered"
            size="small"
            sx={{
              bgcolor: 'rgba(27,94,32,0.08)',
              color: 'primary.main',
              fontWeight: 600,
              fontSize: '0.7rem',
            }}
          />
        </Box>

        <Divider sx={{ mb: 2 }} />

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {items.map((item, i) => (
            <Box
              key={i}
              sx={{
                display: 'flex',
                gap: 1.5,
                p: 1.5,
                borderRadius: 2,
                bgcolor: 'rgba(0,0,0,0.02)',
                '&:hover': { bgcolor: 'rgba(76,175,80,0.04)' },
                transition: 'background 0.15s ease',
              }}
            >
              <LightbulbIcon sx={{ fontSize: 18, color: '#FF8F00', mt: 0.3, flexShrink: 0 }} />
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                {item}
              </Typography>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}
