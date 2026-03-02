let authToken = localStorage.getItem('gs_token') || null;

export function setAuthToken(t) {
  authToken = t;
  if (t) localStorage.setItem('gs_token', t);
  else localStorage.removeItem('gs_token');
}

const BASE_API = 'http://localhost:8000';

export async function apiFetch(path, opts = {}) {
  opts.headers = opts.headers || {};
  if (authToken) opts.headers['Authorization'] = `Bearer ${authToken}`;
  try {
    const res = await fetch(BASE_API + path, opts);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${res.status} ${res.statusText} - ${text}`);
    }
    return await res.json();
  } catch (err) {
    console.error('API error', err);
    throw err;
  }
}
