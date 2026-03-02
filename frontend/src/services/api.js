import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((cfg) => {
  const token = (typeof window !== 'undefined') && window.localStorage?.getItem('gs_token');
  if (token && token !== 'demo') {
    cfg.headers = { ...cfg.headers, Authorization: `Bearer ${token}` };
  }
  return cfg;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const token = window.localStorage?.getItem('gs_token');
      if (token && token !== 'demo') {
        window.localStorage.removeItem('gs_token');
        window.localStorage.removeItem('gs_role');
        window.location.replace('/login');
      }
    }
    return Promise.reject(err);
  },
);

export default api;
