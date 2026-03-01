import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Chip } from '@mui/material';
import { Bar } from 'react-chartjs-2';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

const DEMO_MARKET = {
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
  prices: [2200, 2180, 2250, 2300, 2280],
  crop: 'Rice',
};

export default function MarketChart({ data = DEMO_MARKET }) {
  const prices = data.prices || DEMO_MARKET.prices;
  const crop = data.crop || 'Rice';
  const change = prices.length >= 2
    ? (((prices[prices.length - 1] - prices[0]) / prices[0]) * 100).toFixed(1)
    : 0;

  const chartData = {
    labels: data.labels || DEMO_MARKET.labels,
    datasets: [
      {
        label: `${crop} Price (₹/quintal)`,
        data: prices,
        backgroundColor: prices.map((_, i) =>
          i === prices.length - 1
            ? 'rgba(27, 94, 32, 0.85)'
            : 'rgba(27, 94, 32, 0.25)'
        ),
        borderColor: prices.map((_, i) =>
          i === prices.length - 1 ? '#1B5E20' : 'rgba(27, 94, 32, 0.4)'
        ),
        borderWidth: 1,
        borderRadius: 8,
        barThickness: 36,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (ctx) => `₹${ctx.raw.toLocaleString('en-IN')}/quintal`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: { color: 'rgba(0,0,0,0.04)' },
        ticks: {
          font: { size: 11 },
          callback: (val) => `₹${val.toLocaleString('en-IN')}`,
        },
      },
      x: { grid: { display: false }, ticks: { font: { size: 11, weight: '500' } } },
    },
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUpIcon sx={{ color: '#1B5E20' }} />
            <Typography variant="h6">Market Price — {crop}</Typography>
          </Box>
          <Chip
            label={`${change >= 0 ? '+' : ''}${change}%`}
            size="small"
            sx={{
              bgcolor: change >= 0 ? 'rgba(76,175,80,0.1)' : 'rgba(244,67,54,0.1)',
              color: change >= 0 ? '#2E7D32' : '#D32F2F',
              fontWeight: 700,
            }}
          />
        </Stack>
        <Box sx={{ height: 280 }}>
          <Bar data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
}
