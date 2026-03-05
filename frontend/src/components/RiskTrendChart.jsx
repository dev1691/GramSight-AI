import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Chip } from '@mui/material';
import { Line } from 'react-chartjs-2';
import TimelineIcon from '@mui/icons-material/Timeline';

const DEMO_TREND = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  scores: [42, 48, 55, 51, 63, 58],
};

export default function RiskTrendChart({ data = DEMO_TREND }) {
  const scores = data.scores || DEMO_TREND.scores;
  const latest = scores[scores.length - 1];
  const previous = scores[scores.length - 2];
  const trendDir = latest > previous ? 'Rising' : latest < previous ? 'Falling' : 'Stable';

  const chartData = {
    labels: data.labels || DEMO_TREND.labels,
    datasets: [
      {
        label: 'Avg District Risk',
        data: scores,
        borderColor: '#FF8F00',
        backgroundColor: 'rgba(255, 143, 0, 0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#FF8F00',
        pointBorderWidth: 2.5,
        pointHoverRadius: 7,
      },
      {
        label: 'Warning Threshold',
        data: scores.map(() => 70),
        borderColor: 'rgba(244, 67, 54, 0.4)',
        borderDash: [8, 4],
        borderWidth: 1.5,
        pointRadius: 0,
        fill: false,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: {
        position: 'top',
        align: 'end',
        labels: { usePointStyle: true, padding: 16, font: { size: 11, weight: '500' } },
      },
    },
    scales: {
      y: {
        min: 0, max: 100,
        grid: { color: 'rgba(0,0,0,0.04)' },
        ticks: { font: { size: 11 } },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 11, weight: '500' } },
      },
    },
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimelineIcon sx={{ color: '#FF8F00' }} />
            <Typography variant="h6">District Risk Trend</Typography>
          </Box>
          <Chip
            label={trendDir}
            size="small"
            sx={{
              bgcolor: trendDir === 'Rising' ? 'rgba(244,67,54,0.1)' : 'rgba(76,175,80,0.1)',
              color: trendDir === 'Rising' ? '#D32F2F' : '#2E7D32',
              fontWeight: 600,
            }}
          />
        </Stack>
        <Box sx={{ height: 280 }}>
          <Line data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
}
