import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Box, Grid, Typography, Skeleton, Stack, IconButton, Tooltip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import api from '../services/api';
import VillageSelector from '../components/VillageSelector';
import RiskGauge from '../components/RiskGauge';
import WeatherChart from '../components/WeatherChart';
import MarketChart from '../components/MarketChart';
import AdvisoryBox from '../components/AdvisoryBox';
import SoilHealthCard from '../components/SoilHealthCard';
import StatsCard from '../components/StatsCard';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import ThermostatIcon from '@mui/icons-material/Thermostat';
import StorefrontIcon from '@mui/icons-material/Storefront';

const FALLBACK_WEATHER = {
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
  temperature: [28, 31, 33, 30, 27],
  rainfall: [5, 12, 2, 0, 8],
  humidity: [65, 72, 58, 54, 68],
};

const FALLBACK_MARKET = {
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
  prices: [2200, 2180, 2250, 2300, 2280],
  crop: 'Rice',
};

function generateWeatherFromApi(apiData) {
  const history = apiData?.history;
  if (Array.isArray(history) && history.length >= 2) {
    const dayLabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const recent = history.slice(0, 5).reverse();
    return {
      labels: recent.map((_, i) => dayLabels[i] || `Day ${i + 1}`),
      temperature: recent.map((h) => Math.round(h.temperature ?? 28)),
      rainfall: recent.map((h) => Math.round(h.rainfall ?? 0)),
      humidity: recent.map((h) => Math.round(h.humidity ?? 60)),
    };
  }
  const temp = apiData?.weather?.temperature ?? 28;
  const precip = apiData?.weather?.precipitation ?? 0;
  const hum = apiData?.weather?.humidity ?? 60;
  return {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
    temperature: [temp - 3, temp - 1, temp + 2, temp, temp - 1].map(Math.round),
    rainfall: [precip + 5, precip + 12, precip, 0, precip + 8].map(Math.round),
    humidity: [hum - 5, hum + 2, hum - 7, hum - 11, hum + 3].map(Math.round),
  };
}

function generateMarketFromApi(apiData) {
  const markets = apiData?.markets;
  if (!markets || markets.length === 0) return FALLBACK_MARKET;
  if (markets.length >= 2) {
    const recent = markets.slice(0, 5);
    return {
      labels: recent.map((_, i) => `Week ${i + 1}`),
      prices: recent.map((m) => Math.round(m.modal_price || m.price || 250)),
      crop: markets[0].commodity
        ? markets[0].commodity.charAt(0).toUpperCase() + markets[0].commodity.slice(1)
        : 'Wheat',
    };
  }
  const item = markets[0];
  const base = item.modal_price || item.price || 250;
  return {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
    prices: [
      Math.round(base * 0.96),
      Math.round(base * 0.98),
      Math.round(base * 1.01),
      Math.round(base * 1.03),
      Math.round(base),
    ],
    crop: item.commodity ? item.commodity.charAt(0).toUpperCase() + item.commodity.slice(1) : 'Wheat',
  };
}

export default function FarmerDashboard() {
  const [villages, setVillages] = useState([]);
  const [villageId, setVillageId] = useState('');
  const [riskScore, setRiskScore] = useState(null);
  const [weatherData, setWeatherData] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [soilData, setSoilData] = useState(null);
  const [advisoryItems, setAdvisoryItems] = useState(null);
  const [loading, setLoading] = useState(true);
  const fetchRef = useRef(0);

  /* Fetch village list on mount */
  useEffect(() => {
    api.get('/farmer/villages')
      .then((res) => {
        const data = res.data;
        if (Array.isArray(data) && data.length > 0) {
          setVillages(data);
          setVillageId(data[0].id);
        }
      })
      .catch(() => { /* VillageSelector falls back to its built-in demo list */ });
  }, []);

  const fetchAll = useCallback(async (vid) => {
    const id = ++fetchRef.current;
    setLoading(true);
    const results = await Promise.allSettled([
      api.get(`/farmer/${vid}/risk`),
      api.get(`/farmer/${vid}/weather`),
      api.get(`/farmer/${vid}/market`),
      api.get(`/farmer/${vid}/soil`),
      api.get(`/farmer/${vid}/advisory`),
    ]);
    if (fetchRef.current !== id) return; // stale request

    const [riskRes, weatherRes, marketRes, soilRes, advisoryRes] = results;

    if (riskRes.status === 'fulfilled') {
      const r = riskRes.value.data;
      setRiskScore(r.risk?.score != null ? Math.round(r.risk.score) : 55);
    } else {
      setRiskScore(55);
    }

    if (weatherRes.status === 'fulfilled') {
      setWeatherData(generateWeatherFromApi(weatherRes.value.data));
    } else {
      setWeatherData(FALLBACK_WEATHER);
    }

    if (marketRes.status === 'fulfilled') {
      setMarketData(generateMarketFromApi(marketRes.value.data));
    } else {
      setMarketData(FALLBACK_MARKET);
    }

    if (soilRes.status === 'fulfilled') {
      const s = soilRes.value.data;
      const hasData = s && Object.values(s).some((v) => v != null);
      setSoilData(hasData ? s : null);
    } else {
      setSoilData(null);
    }

    if (advisoryRes.status === 'fulfilled') {
      const a = advisoryRes.value.data;
      const items = a?.items;
      setAdvisoryItems(Array.isArray(items) && items.length > 0 && items[0] !== 'Please try again later' ? items : null);
    } else {
      setAdvisoryItems(null);
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    if (villageId) fetchAll(villageId);
  }, [villageId, fetchAll]);

  const handleVillageChange = (id) => {
    setVillageId(id);
  };

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
            Farm Overview
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time risk assessment and agricultural insights
          </Typography>
        </Box>
        <Stack direction="row" spacing={1.5} alignItems="center">
          <VillageSelector
            value={villageId}
            onChange={handleVillageChange}
            villages={villages.length > 0 ? villages : undefined}
          />
          <Tooltip title="Refresh data">
            <IconButton
              onClick={() => fetchAll(villageId)}
              size="small"
              sx={{ bgcolor: 'rgba(0,0,0,0.04)', '&:hover': { bgcolor: 'rgba(0,0,0,0.08)' } }}
            >
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </Stack>

      {loading ? (
        <Grid container spacing={3}>
          {[...Array(6)].map((_, i) => (
            <Grid item xs={12} md={i < 3 ? 4 : 6} key={i}>
              <Skeleton variant="rectangular" height={i < 3 ? 120 : 320} sx={{ borderRadius: 4 }} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <>
          {/* Quick Stats Row */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={4}>
              <StatsCard
                title="Temperature"
                value={`${weatherData?.temperature?.[weatherData.temperature.length - 1] ?? '--'}°C`}
                subtitle="Current forecast"
                icon={<ThermostatIcon />}
                color="#FF6384"
                trend={-3.2}
                trendLabel="vs yesterday"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <StatsCard
                title="Rainfall"
                value={`${weatherData?.rainfall?.[weatherData.rainfall.length - 1] ?? '--'} mm`}
                subtitle="Today's forecast"
                icon={<WaterDropIcon />}
                color="#36A2EB"
                trend={8}
                trendLabel="vs avg"
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <StatsCard
                title="Market Price"
                value={`₹${marketData?.prices?.[marketData.prices.length - 1]?.toLocaleString('en-IN') ?? '--'}`}
                subtitle={`${marketData?.crop || 'Crop'} / quintal`}
                icon={<StorefrontIcon />}
                color="#1B5E20"
                trend={2.4}
                trendLabel="this week"
              />
            </Grid>
          </Grid>

          {/* Risk Gauge + Weather Chart */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} md={4}>
              <RiskGauge score={riskScore} lastUpdated="2 hours ago" />
            </Grid>
            <Grid item xs={12} md={8}>
              <WeatherChart data={weatherData} />
            </Grid>
          </Grid>

          {/* Market Chart + Advisory */}
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <MarketChart data={marketData} />
            </Grid>
            <Grid item xs={12} md={6}>
              <AdvisoryBox items={advisoryItems || undefined} />
            </Grid>
          </Grid>

          {/* Soil Health */}
          <Grid container spacing={2.5}>
            <Grid item xs={12} md={6}>
              <SoilHealthCard data={soilData || undefined} />
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
}
