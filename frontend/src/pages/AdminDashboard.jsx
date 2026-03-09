import React, { useEffect, useState, useCallback } from 'react';
import {
  Box, Grid, Typography, Skeleton, Stack, IconButton, Tooltip, Chip,
  Card, CardContent, LinearProgress, Divider, CircularProgress,
  FormControl, InputLabel, Select, MenuItem,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import LocationCityIcon from '@mui/icons-material/LocationCity';
import GroupsIcon from '@mui/icons-material/Groups';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import SpeedIcon from '@mui/icons-material/Speed';
import GrassIcon from '@mui/icons-material/Grass';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import LandscapeIcon from '@mui/icons-material/Landscape';
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

function riskColor(score) {
  if (score <= 30) return '#4CAF50';
  if (score <= 60) return '#FF9800';
  if (score <= 80) return '#F44336';
  return '#B71C1C';
}

/* ── Crop Distribution Mini-Chart ────────────────────────────── */
function CropDistribution({ villages }) {
  const cropCounts = {};
  villages.forEach((v) => {
    const c = v.crop || 'Other';
    cropCounts[c] = (cropCounts[c] || 0) + 1;
  });
  const entries = Object.entries(cropCounts).sort((a, b) => b[1] - a[1]);
  const total = villages.length || 1;
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4', '#795548', '#607D8B'];
  return (
    <Card sx={{ borderRadius: 4, border: '1px solid rgba(0,0,0,0.08)', height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <GrassIcon sx={{ color: '#4CAF50', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
            Crop Distribution
          </Typography>
        </Stack>
        <Stack spacing={1.5}>
          {entries.map(([crop, count], i) => (
            <Box key={crop}>
              <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.3 }}>
                <Typography variant="body2" sx={{ fontWeight: 500 }}>{crop}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {count} village{count > 1 ? 's' : ''} ({Math.round(count / total * 100)}%)
                </Typography>
              </Stack>
              <LinearProgress
                variant="determinate"
                value={count / total * 100}
                sx={{
                  height: 8, borderRadius: 4, bgcolor: 'rgba(0,0,0,0.06)',
                  '& .MuiLinearProgress-bar': { bgcolor: colors[i % colors.length], borderRadius: 4 },
                }}
              />
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}

/* ── Village Overview Cards ──────────────────────────────────── */
function VillageOverviewCards({ villages }) {
  const top4 = [...villages].sort((a, b) => b.score - a.score).slice(0, 4);
  return (
    <Card sx={{ borderRadius: 4, border: '1px solid rgba(0,0,0,0.08)', height: '100%' }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <LocationCityIcon sx={{ color: '#0288D1', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
            Village Overview
          </Typography>
        </Stack>
        <Stack spacing={1.5}>
          {top4.map((v) => (
            <Box key={v.id} sx={{
              p: 1.5, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.02)',
              border: `1px solid ${riskColor(v.score)}20`,
            }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 700 }}>{v.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {v.district} &middot; {v.crop}
                  </Typography>
                </Box>
                <Chip
                  label={`${v.score}%`}
                  size="small"
                  sx={{
                    bgcolor: `${riskColor(v.score)}15`,
                    color: riskColor(v.score),
                    fontWeight: 700, fontSize: 12,
                    border: `1px solid ${riskColor(v.score)}30`,
                  }}
                />
              </Stack>
            </Box>
          ))}
        </Stack>
      </CardContent>
    </Card>
  );
}

/* ── Farmland Summary Card ───────────────────────────────────── */
function FarmlandSummary({ data }) {
  if (!data) return null;
  return (
    <Card sx={{ borderRadius: 4, border: '1px solid rgba(0,0,0,0.08)' }}>
      <CardContent sx={{ p: 3 }}>
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
          <LandscapeIcon sx={{ color: '#795548', fontSize: 20 }} />
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
            Farm Registry
          </Typography>
        </Stack>
        <Grid container spacing={2}>
          <Grid item xs={4}>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#1B5E20' }}>{data.total_farmlands}</Typography>
            <Typography variant="caption" color="text.secondary">Total Plots</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="h4" sx={{ fontWeight: 800, color: '#0288D1' }}>{data.total_acres}</Typography>
            <Typography variant="caption" color="text.secondary">Total Acres</Typography>
          </Grid>
          <Grid item xs={4}>
            <Typography variant="h4" sx={{ fontWeight: 800, color: riskColor(data.avg_risk_score || 0) }}>
              {data.avg_risk_score != null ? `${Math.round(data.avg_risk_score)}%` : 'N/A'}
            </Typography>
            <Typography variant="caption" color="text.secondary">Avg Risk</Typography>
          </Grid>
        </Grid>
        {data.crop_distribution && data.crop_distribution.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Divider sx={{ mb: 1.5 }} />
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
              Top Crops Registered
            </Typography>
            <Stack direction="row" spacing={0.5} flexWrap="wrap">
              {data.crop_distribution.slice(0, 5).map((c) => (
                <Chip key={c.crop} label={`${c.crop} (${c.count})`} size="small" variant="outlined"
                  sx={{ fontSize: 11, mb: 0.5 }} />
              ))}
            </Stack>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default function AdminDashboard() {
  const [villages, setVillages] = useState([]);
  const [marketTrendData, setMarketTrendData] = useState(null);
  const [riskTrendData, setRiskTrendData] = useState(null);
  const [farmerCount, setFarmerCount] = useState(null);
  const [farmlandSummary, setFarmlandSummary] = useState(null);
  const [aiInsight, setAiInsight] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [availableCrops, setAvailableCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    const marketUrl = selectedCrop
      ? `/admin/market-trend?commodity=${encodeURIComponent(selectedCrop)}`
      : '/admin/market-trend';
    const results = await Promise.allSettled([
      api.get('/admin/villages'),
      api.get(marketUrl),
      api.get('/admin/risk-trend'),
      api.get('/admin/stats'),
      api.get('/farmland/admin/summary'),
      api.get('/admin/crops'),
    ]);

    const [villagesRes, marketRes, riskRes, statsRes, farmlandRes, cropsRes] = results;

    // Villages
    if (villagesRes.status === 'fulfilled') {
      const apiVillages = villagesRes.value.data;
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
    } else {
      setVillages(DEMO_VILLAGES);
    }

    if (marketRes.status === 'fulfilled') {
      const mt = marketRes.value.data;
      if (mt && Array.isArray(mt.labels) && mt.labels.length > 0) setMarketTrendData(mt);
    }

    if (riskRes.status === 'fulfilled') {
      const rt = riskRes.value.data;
      if (rt && Array.isArray(rt.labels) && rt.labels.length > 0) setRiskTrendData(rt);
    }

    if (statsRes.status === 'fulfilled') {
      const st = statsRes.value.data;
      if (st?.farmer_count != null) setFarmerCount(st.farmer_count);
    }

    if (farmlandRes.status === 'fulfilled') {
      setFarmlandSummary(farmlandRes.value.data);
    }

    if (cropsRes.status === 'fulfilled') {
      const crops = cropsRes.value.data?.crops;
      setAvailableCrops(Array.isArray(crops) ? crops : []);
    } else {
      setAvailableCrops([]);
    }

    setLoading(false);
  }, [selectedCrop]);

  const fetchAiInsight = async (villageId) => {
    setAiLoading(true);
    try {
      const res = await api.post(`/ai/admin/ai-analysis/${villageId}`);
      setAiInsight(res.data);
    } catch {
      setAiInsight({ summary: 'AI analysis temporarily unavailable', is_fallback: true });
    }
    setAiLoading(false);
  };

  useEffect(() => { fetchData(); }, [fetchData]);

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
        <Stack direction="row" spacing={1.5} alignItems="center" flexWrap="wrap" useFlexGap>
          <Chip label="Pune District" variant="outlined" size="small" sx={{ fontWeight: 600 }} />
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <InputLabel id="admin-crop-select-label">Market Crop</InputLabel>
            <Select
              labelId="admin-crop-select-label"
              value={selectedCrop}
              label="Market Crop"
              onChange={(e) => setSelectedCrop(e.target.value)}
            >
              <MenuItem value="">
                <em>All crops</em>
              </MenuItem>
              {availableCrops.map((c) => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </Select>
          </FormControl>
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
                value={farmerCount != null ? farmerCount.toLocaleString('en-IN') : '1,240'}
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
              <VillageRiskTable villages={villages} onSelect={(v) => fetchAiInsight(v.id)} />
            </Grid>
            <Grid item xs={12} md={4}>
              <HighRiskAlerts alerts={alerts} />
            </Grid>
          </Grid>

          {/* Crop Distribution + Village Overview + Farmland Summary */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <CropDistribution villages={villages} />
            </Grid>
            <Grid item xs={12} md={4}>
              <VillageOverviewCards villages={villages} />
            </Grid>
            <Grid item xs={12} md={4}>
              <FarmlandSummary data={farmlandSummary} />
            </Grid>
          </Grid>

          {/* AI Insight Panel */}
          {(aiInsight || aiLoading) && (
            <Card sx={{ borderRadius: 4, border: '1px solid rgba(0,0,0,0.08)', mb: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
                  <AutoAwesomeIcon sx={{ color: '#7B1FA2', fontSize: 20 }} />
                  <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
                    Village AI Insights
                  </Typography>
                  {aiInsight?.is_fallback && (
                    <Chip label="Fallback" size="small" color="warning" variant="outlined" sx={{ fontSize: 10 }} />
                  )}
                </Stack>
                {aiLoading ? (
                  <Stack direction="row" spacing={2} alignItems="center">
                    <CircularProgress size={20} />
                    <Typography variant="body2" color="text.secondary">Generating AI analysis...</Typography>
                  </Stack>
                ) : (
                  <Grid container spacing={2}>
                    {aiInsight?.weather_analysis && (
                      <Grid item xs={12} md={4}>
                        <Box sx={{ p: 2, bgcolor: '#E3F2FD', borderRadius: 2 }}>
                          <Typography variant="caption" sx={{ fontWeight: 700, color: '#1565C0' }}>Weather Analysis</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5, fontSize: 12 }}>{aiInsight.weather_analysis}</Typography>
                        </Box>
                      </Grid>
                    )}
                    {aiInsight?.market_analysis && (
                      <Grid item xs={12} md={4}>
                        <Box sx={{ p: 2, bgcolor: '#E8F5E9', borderRadius: 2 }}>
                          <Typography variant="caption" sx={{ fontWeight: 700, color: '#2E7D32' }}>Market Analysis</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5, fontSize: 12 }}>{aiInsight.market_analysis}</Typography>
                        </Box>
                      </Grid>
                    )}
                    {aiInsight?.risk_assessment && (
                      <Grid item xs={12} md={4}>
                        <Box sx={{ p: 2, bgcolor: '#FFF3E0', borderRadius: 2 }}>
                          <Typography variant="caption" sx={{ fontWeight: 700, color: '#E65100' }}>Risk Assessment</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5, fontSize: 12 }}>{aiInsight.risk_assessment}</Typography>
                        </Box>
                      </Grid>
                    )}
                    {aiInsight?.summary && (
                      <Grid item xs={12}>
                        <Box sx={{ p: 2, bgcolor: '#F3E5F5', borderRadius: 2 }}>
                          <Typography variant="caption" sx={{ fontWeight: 700, color: '#7B1FA2' }}>Summary</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5, fontSize: 12 }}>{aiInsight.summary}</Typography>
                        </Box>
                      </Grid>
                    )}
                    {aiInsight?.recommendations && Array.isArray(aiInsight.recommendations) && (
                      <Grid item xs={12}>
                        <Typography variant="caption" sx={{ fontWeight: 700, color: '#1B2A3D', mb: 1, display: 'block' }}>
                          Recommendations
                        </Typography>
                        <Stack spacing={0.5}>
                          {aiInsight.recommendations.map((r, i) => (
                            <Typography key={i} variant="body2" sx={{
                              fontSize: 12, pl: 1.5, borderLeft: '3px solid #7B1FA2',
                              color: '#4A148C',
                            }}>
                              {r}
                            </Typography>
                          ))}
                        </Stack>
                      </Grid>
                    )}
                  </Grid>
                )}
              </CardContent>
            </Card>
          )}

          {/* Risk Trend + Market */}
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6}>
              <RiskTrendChart data={riskTrendData || undefined} />
            </Grid>
            <Grid item xs={12} md={6}>
              <MarketChart data={marketTrendData || DEMO_MARKET_ADMIN} />
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
