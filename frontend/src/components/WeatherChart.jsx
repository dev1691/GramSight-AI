import React from 'react';
import { Card, CardContent, Typography, Box, Stack, Chip } from '@mui/material';
import { Line } from 'react-chartjs-2';
import WbSunnyIcon from '@mui/icons-material/WbSunny';

const DEMO_WEATHER = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  temperature: [28, 31, 33, 30, 27],
  rainfall: [5, 12, 2, 0, 8],
  humidity: [65, 72, 58, 54, 68],
};

export default function WeatherChart({ data = DEMO_WEATHER }) {
  const chartData = {
    labels: data.labels,
    datasets: [
      {
        label: 'Temperature (°C)',
        data: data.temperature,
        borderColor: '#FF6384',
        backgroundColor: 'rgba(255, 99, 132, 0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#FF6384',
        pointBorderWidth: 2,
        yAxisID: 'y',
      },
      {
        label: 'Rainfall (mm)',
        data: data.rainfall,
        borderColor: '#36A2EB',
        backgroundColor: 'rgba(54, 162, 235, 0.08)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointBackgroundColor: '#fff',
        pointBorderColor: '#36A2EB',
        pointBorderWidth: 2,
        yAxisID: 'y1',
      },
      {
        label: 'Humidity (%)',
        data: data.humidity,
        borderColor: '#4BC0C0',
        backgroundColor: 'transparent',
        fill: false,
        tension: 0.4,
        borderDash: [6, 4],
        pointRadius: 3,
        pointBackgroundColor: '#4BC0C0',
        yAxisID: 'y',
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
        position: 'left',
        grid: { color: 'rgba(0,0,0,0.04)' },
        ticks: { font: { size: 11 } },
      },
      y1: {
        position: 'right',
        grid: { display: false },
        ticks: { font: { size: 11 } },
      },
      x: {
        grid: { display: false },
        ticks: { font: { size: 11, weight: '500' } },
      },
    },
  };

  const avgTemp = data.temperature.length
    ? (data.temperature.reduce((a, b) => a + b, 0) / data.temperature.length).toFixed(1)
    : '--';

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <WbSunnyIcon sx={{ color: '#FF8F00' }} />
            <Typography variant="h6">5-Day Weather Trend</Typography>
          </Box>
          <Chip label={`Avg ${avgTemp}°C`} size="small" variant="outlined" />
        </Stack>
        <Box sx={{ height: 280 }}>
          <Line data={chartData} options={options} />
        </Box>
      </CardContent>
    </Card>
  );
}
