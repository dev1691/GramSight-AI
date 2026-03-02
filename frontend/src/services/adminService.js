import api from './api';

export const getVillages = () => api.get('/admin/villages');

export const getMarketTrend = () => api.get('/admin/market-trend');

export const getRiskTrend = () => api.get('/admin/risk-trend');

export const getStats = () => api.get('/admin/stats');
