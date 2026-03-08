import api from './api';

export const getVillages = () => api.get('/farmer/villages');

export const getRisk = (villageId) => api.get(`/farmer/${villageId}/risk`);

export const getWeather = (villageId) => api.get(`/farmer/${villageId}/weather`);

export const getMarket = (villageId) => api.get(`/farmer/${villageId}/market`);

export const getSoil = (villageId) => api.get(`/farmer/${villageId}/soil`);

export const getAdvisory = (villageId) => api.get(`/farmer/${villageId}/advisory`);
