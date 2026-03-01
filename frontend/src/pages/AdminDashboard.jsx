import React, { useEffect, useState, useCallback } from 'react';
import { Box, Grid, Typography, Skeleton, Stack, IconButton, Tooltip, Chip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import LocationCityIcon from '@mui/icons-material/LocationCity';
import GroupsIcon from '@mui/icons-material/Groups';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import SpeedIcon from '@mui/icons-material/Speed';
import api from '../services/api';
import StatsCard from '../components/StatsCard';
import VillageRiskTable from '../components/VillageRiskTable';
import HighRiskAlerts from '../components/HighRiskAlerts';
import RiskTrendChart from '../components/RiskTrendChart';
import MarketChart from '../components/MarketChart';

const DEMO_VILLAGES = [
  { id: 1, name: 'Rajpur', district: 'Pune', score: 72, crop: 'Rice' },
  { id: 2, name: 'Devgad', district: 'Sindhudurg', score: 45, crop: 'Mango' },
  { id: 3, name: 'Malshiras', district: 'Solapur', score: 83, crop: 'Sugarcane' },
  { id: 4, name: 'Kothrud', district: 'Pune', score: 28, crop: 'Wheat' },
  { id: 5, name: 'Sinhagad', district: 'Pune', score: 56, crop: 'Soybean' },
  { id: 6, name: 'Baramati', district: 'Pune', score: 91, crop: 'Sugarcane' },
  { id: 7, name: 'Pandharpur', district: 'Solapur', score: 67, crop: 'Jowar' },
  { id: 8, name: 'Wai', district: 'Satara', score: 34, crop: 'Strawberry' },
];

const DEMO_MARKET_ADMIN = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
  prices: [2100, 2200, 2150, 2300, 2250, 2400],
  crop: 'Rice (District Avg)',
};

export default function AdminDashboard() {
  const [villages, setVillages] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.get('/admin/villages');
      const apiVillages = res.data;
      if (Array.isArray(apiVillages) && apiVillages.length > 0) {
        const enriched = apiVillages.map((v, i) => ({
          id: v.id || i + 1,
          name: v.name || `Village ${i + 1}`,
          district: v.district || 'Unknown',
          score: v.risk_score ?? DEMO_VILLAGES[i % DEMO_VILLAGES.length]?.score ?? 50,
          crop: v.crop || DEMO_VILLAGES[i % DEMO_VILLAGES.length]?.crop || 'Mixed',
        }));
        setVillages(enriched);
      } else {
        setVillages(DEMO_VILLAGES);
      }
    } catch {
      setVillages(DEMO_VILLAGES);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const totalVillages = villages.length;
  const avgRisk = villages.length
    ? Math.round(villages.reduce((s, v) => s + v.score, 0) / villages.length)
    : 0;
  const highRiskVillages = villages.filter((v) => v.score > 70);
  const highRiskCount = highRiskVillages.length;
  const alerts = highRiskVillages
    .sort((a, b) => b.score - a.score)
    .map((v) => ({
      id: v.id,
      name: v.name,
      score: v.score,
      reason: v.score > 85
        ? 'Critically high risk — immediate action required'
        : 'Risk score exceeds safety threshold',
    }));

  return (
    <Box>
      {/* Header */}
      <Stack
        direction={{ xs: 'column', sm: 'row' }}
        justifyContent="space-between"
        alignItems={{ xs: 'flex-start', sm: 'center' }}
        spacing={2}
        sx={{ mb: 3 }}
      >
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
            District Overview
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Multi-village risk monitoring and policy analytics
          </Typography>
        </Box>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <Chip label="Pune District" variant="outlined" size="small" sx={{ fontWeight: 600 }} />
          <Tooltip title="Refresh data">
            <IconButton
              onClick={fetchData}
              size="small"
              sx={{ bgcolor: 'rgba(0,0,0,0.04)', '&:hover': { bgcolor: 'rgba(0,0,0,0.08)' } }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      {loading ? (
        <Grid container spacing={2.5}>
          {[...Array(4)].map((_, i) => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={130} sx={{ borderRadius: 4 }} />
            </Grid>
          ))}
          <Grid item xs={12} md={8}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 4 }} />
          </Grid>
          <Grid item xs={12} md={4}>
            <Skeleton variant="rectangular" height={400} sx={{ borderRadius: 4 }} />
          </Grid>
        </Grid>
      ) : (
        <>
          {/* KPI Stats Row */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard
                title="Total Villages"
                value={totalVillages}
                subtitle="Under monitoring"
                icon={<LocationCityIcon />}
                color="#0288D1"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard
                title="Avg Risk Score"
                value={avgRisk}
                subtitle="District average"
                icon={<SpeedIcon />}
                color="#FF8F00"
                trend={4.2}
                trendLabel="vs last month"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard
                title="High Risk"
                value={highRiskCount}
                subtitle="Villages > 70 score"
                icon={<WarningAmberIcon />}
                color="#D32F2F"
                trend={highRiskCount > 2 ? 12 : -5}
                trendLabel="vs last week"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard
                title="Farmers Covered"
                value="1,240"
                subtitle="Active beneficiaries"
                icon={<GroupsIcon />}
                color="#2E7D32"
                trend={6.8}
                trendLabel="this quarter"
              />
            </Grid>
          </Grid>

          {/* Village Table + High Risk Alerts */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} md={8}>
              <VillageRiskTable villages={villages} />
            </Grid>
            <Grid item xs={12} md={4}>
              <HighRiskAlerts alerts={alerts} />
            </Grid>
          </Grid>

          {/* Risk Trend + Market */}
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6}>
              <RiskTrendChart />
            </Grid>
            <Grid item xs={12} md={6}>
              <MarketChart data={DEMO_MARKET_ADMIN} />
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
