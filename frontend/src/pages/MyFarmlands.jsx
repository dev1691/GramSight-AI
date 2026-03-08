import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, MenuItem, Stack, Chip, IconButton,
  Tooltip, Skeleton, Alert, CircularProgress, LinearProgress, Divider,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import LandscapeIcon from '@mui/icons-material/Landscape';
import GrassIcon from '@mui/icons-material/Grass';
import WaterDropIcon from '@mui/icons-material/WaterDrop';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import RefreshIcon from '@mui/icons-material/Refresh';
import api from '../services/api';

const SOIL_TYPES = ['Alluvial', 'Black (Regur)', 'Red', 'Laterite', 'Sandy', 'Clayey', 'Loamy', 'Other'];
const IRRIGATION_TYPES = ['Drip', 'Sprinkler', 'Canal', 'Borewell', 'Rainfed', 'Flood', 'Other'];
const CROP_TYPES = ['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Soybean', 'Jowar', 'Bajra', 'Maize', 'Mango', 'Onion', 'Tomato', 'Groundnut', 'Paddy', 'Other'];

function riskColor(level) {
  if (!level) return '#9E9E9E';
  const l = level.toLowerCase();
  if (l === 'low') return '#4CAF50';
  if (l === 'moderate') return '#FF9800';
  if (l === 'high') return '#F44336';
  return '#B71C1C';
}

function RiskBadge({ score, level }) {
  if (score == null) return null;
  const color = riskColor(level);
  return (
    <Chip
      label={`${Math.round(score)}% ${level || ''}`}
      size="small"
      sx={{
        bgcolor: `${color}18`,
        color,
        fontWeight: 700,
        border: `1px solid ${color}40`,
        fontSize: 12,
      }}
    />
  );
}

const emptyForm = {
  land_name: '', total_acres: '', soil_type: '', irrigation_type: '',
  crop_type: '', sowing_date: '', harvest_date: '', village_id: '',
  geo_lat: '', geo_lng: '', notes: '',
};

export default function MyFarmlands() {
  const [farmlands, setFarmlands] = useState([]);
  const [villages, setVillages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [insightLoading, setInsightLoading] = useState({});

  const fetchFarmlands = useCallback(async () => {
    setLoading(true);
    try {
      const [flRes, vRes] = await Promise.all([
        api.get('/farmland/'),
        api.get('/farmer/villages'),
      ]);
      setFarmlands(flRes.data || []);
      setVillages(Array.isArray(vRes.data) ? vRes.data : []);
    } catch {
      setError('Failed to load farmlands');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchFarmlands(); }, [fetchFarmlands]);

  const handleChange = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async () => {
    if (!form.land_name || !form.total_acres) {
      setError('Land name and total acres are required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const payload = {
        ...form,
        total_acres: parseFloat(form.total_acres),
        geo_lat: form.geo_lat ? parseFloat(form.geo_lat) : null,
        geo_lng: form.geo_lng ? parseFloat(form.geo_lng) : null,
        sowing_date: form.sowing_date || null,
        harvest_date: form.harvest_date || null,
        village_id: form.village_id || null,
      };
      await api.post('/farmland/', payload);
      setDialogOpen(false);
      setForm(emptyForm);
      fetchFarmlands();
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create farmland');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this farmland?')) return;
    try {
      await api.delete(`/farmland/${id}`);
      setFarmlands((prev) => prev.filter((f) => f.id !== id));
    } catch { /* ignore */ }
  };

  const handleAiInsight = async (id) => {
    setInsightLoading((prev) => ({ ...prev, [id]: true }));
    try {
      const res = await api.post(`/farmland/${id}/ai-insight`);
      setFarmlands((prev) => prev.map((f) => f.id === id ? res.data : f));
    } catch { /* ignore */ }
    setInsightLoading((prev) => ({ ...prev, [id]: false }));
  };

  return (
    <Box>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, color: '#1B2A3D' }}>
            My Farmlands
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Register and manage your farmland plots
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchFarmlands} size="small"
              sx={{ bgcolor: 'rgba(0,0,0,0.04)', '&:hover': { bgcolor: 'rgba(0,0,0,0.08)' } }}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}
            sx={{ borderRadius: 2, textTransform: 'none', fontWeight: 600 }}>
            Add Farmland
          </Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      {/* Farmland Cards */}
      {loading ? (
        <Grid container spacing={2.5}>
          {[0, 1, 2].map((i) => (
            <Grid item xs={12} md={6} lg={4} key={i}>
              <Skeleton variant="rectangular" height={300} sx={{ borderRadius: 4 }} />
            </Grid>
          ))}
        </Grid>
      ) : farmlands.length === 0 ? (
        <Card sx={{ p: 6, textAlign: 'center', borderRadius: 4, border: '2px dashed rgba(0,0,0,0.12)' }}>
          <LandscapeIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No Farmlands Registered
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Click "Add Farmland" to register your first plot and get AI-powered insights.
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialogOpen(true)}>
            Add Your First Farmland
          </Button>
        </Card>
      ) : (
        <Grid container spacing={2.5}>
          {farmlands.map((f) => (
            <Grid item xs={12} md={6} lg={4} key={f.id}>
              <Card sx={{
                borderRadius: 4, height: '100%', display: 'flex', flexDirection: 'column',
                border: '1px solid rgba(0,0,0,0.08)',
                transition: 'box-shadow 0.2s', '&:hover': { boxShadow: '0 4px 20px rgba(0,0,0,0.08)' },
              }}>
                <CardContent sx={{ flex: 1, p: 3 }}>
                  {/* Header */}
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#1B2A3D', fontSize: 16 }}>
                        {f.land_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {f.village_name || 'No village'} &middot; {f.total_acres} acres
                      </Typography>
                    </Box>
                    <RiskBadge score={f.risk_score} level={f.risk_level} />
                  </Stack>

                  {/* Details */}
                  <Stack spacing={1} sx={{ mb: 2 }}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <GrassIcon sx={{ fontSize: 16, color: '#4CAF50' }} />
                      <Typography variant="body2"><b>Crop:</b> {f.crop_type || 'Not specified'}</Typography>
                    </Stack>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <WaterDropIcon sx={{ fontSize: 16, color: '#2196F3' }} />
                      <Typography variant="body2"><b>Irrigation:</b> {f.irrigation_type || 'Not specified'}</Typography>
                    </Stack>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <LandscapeIcon sx={{ fontSize: 16, color: '#795548' }} />
                      <Typography variant="body2"><b>Soil:</b> {f.soil_type || 'Not specified'}</Typography>
                    </Stack>
                    {f.sowing_date && (
                      <Stack direction="row" spacing={1} alignItems="center">
                        <CalendarMonthIcon sx={{ fontSize: 16, color: '#FF9800' }} />
                        <Typography variant="body2"><b>Sowing:</b> {new Date(f.sowing_date).toLocaleDateString()}</Typography>
                      </Stack>
                    )}
                  </Stack>

                  {/* AI Insight */}
                  {f.ai_insight && (
                    <>
                      <Divider sx={{ my: 1.5 }} />
                      <Box sx={{ bgcolor: '#F3E5F5', borderRadius: 2, p: 1.5, mb: 1 }}>
                        <Stack direction="row" spacing={0.5} alignItems="center" sx={{ mb: 0.5 }}>
                          <AutoAwesomeIcon sx={{ fontSize: 14, color: '#7B1FA2' }} />
                          <Typography variant="caption" sx={{ fontWeight: 700, color: '#7B1FA2' }}>
                            AI INSIGHT
                          </Typography>
                        </Stack>
                        <Typography variant="body2" sx={{ fontSize: 12, color: '#4A148C', lineHeight: 1.5 }}>
                          {f.ai_insight.summary || 'Analysis available'}
                        </Typography>
                        {f.ai_insight.recommendations && (
                          <Box sx={{ mt: 1 }}>
                            {f.ai_insight.recommendations.slice(0, 2).map((r, i) => (
                              <Typography key={i} variant="body2" sx={{ fontSize: 11, color: '#6A1B9A', pl: 1, borderLeft: '2px solid #CE93D8', mb: 0.5 }}>
                                {r}
                              </Typography>
                            ))}
                          </Box>
                        )}
                      </Box>
                    </>
                  )}

                  {/* Risk Bar */}
                  {f.risk_score != null && (
                    <Box sx={{ mt: 1 }}>
                      <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.5 }}>
                        <Typography variant="caption" color="text.secondary">Risk Score</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700, color: riskColor(f.risk_level) }}>
                          {Math.round(f.risk_score)}%
                        </Typography>
                      </Stack>
                      <LinearProgress
                        variant="determinate"
                        value={f.risk_score}
                        sx={{
                          height: 6, borderRadius: 3,
                          bgcolor: 'rgba(0,0,0,0.06)',
                          '& .MuiLinearProgress-bar': { bgcolor: riskColor(f.risk_level), borderRadius: 3 },
                        }}
                      />
                    </Box>
                  )}
                </CardContent>

                {/* Actions */}
                <Stack direction="row" spacing={1} sx={{ px: 3, pb: 2 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={insightLoading[f.id] ? <CircularProgress size={14} /> : <AutoAwesomeIcon />}
                    onClick={() => handleAiInsight(f.id)}
                    disabled={insightLoading[f.id]}
                    sx={{ flex: 1, textTransform: 'none', borderRadius: 2, fontSize: 12 }}
                  >
                    {insightLoading[f.id] ? 'Analyzing...' : 'Get AI Insight'}
                  </Button>
                  <Tooltip title="Delete">
                    <IconButton size="small" color="error" onClick={() => handleDelete(f.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Stack>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Add Farmland Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ fontWeight: 700 }}>Add New Farmland</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField label="Land Name" value={form.land_name} onChange={handleChange('land_name')}
              fullWidth required placeholder="e.g., Green Valley Plot" />
            <TextField label="Total Acres" value={form.total_acres} onChange={handleChange('total_acres')}
              type="number" fullWidth required placeholder="e.g., 3.5" inputProps={{ step: '0.1', min: '0.1' }} />
            <Stack direction="row" spacing={2}>
              <TextField select label="Soil Type" value={form.soil_type} onChange={handleChange('soil_type')} fullWidth>
                {SOIL_TYPES.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </TextField>
              <TextField select label="Irrigation" value={form.irrigation_type} onChange={handleChange('irrigation_type')} fullWidth>
                {IRRIGATION_TYPES.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
              </TextField>
            </Stack>
            <TextField select label="Crop Type" value={form.crop_type} onChange={handleChange('crop_type')} fullWidth>
              {CROP_TYPES.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </TextField>
            <Stack direction="row" spacing={2}>
              <TextField label="Sowing Date" type="date" value={form.sowing_date}
                onChange={handleChange('sowing_date')} fullWidth InputLabelProps={{ shrink: true }} />
              <TextField label="Expected Harvest" type="date" value={form.harvest_date}
                onChange={handleChange('harvest_date')} fullWidth InputLabelProps={{ shrink: true }} />
            </Stack>
            <TextField select label="Village" value={form.village_id} onChange={handleChange('village_id')} fullWidth>
              <MenuItem value="">None</MenuItem>
              {villages.map((v) => <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>)}
            </TextField>
            <Stack direction="row" spacing={2}>
              <TextField label="Latitude" value={form.geo_lat} onChange={handleChange('geo_lat')}
                type="number" fullWidth placeholder="e.g., 18.52" />
              <TextField label="Longitude" value={form.geo_lng} onChange={handleChange('geo_lng')}
                type="number" fullWidth placeholder="e.g., 73.85" />
            </Stack>
            <TextField label="Notes" value={form.notes} onChange={handleChange('notes')}
              fullWidth multiline rows={2} placeholder="Any additional notes..." />
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => setDialogOpen(false)} sx={{ textTransform: 'none' }}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit} disabled={saving}
            startIcon={saving ? <CircularProgress size={16} /> : <AddIcon />}
            sx={{ textTransform: 'none', borderRadius: 2 }}>
            {saving ? 'Saving...' : 'Add Farmland'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
