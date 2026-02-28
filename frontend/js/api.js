let authToken = localStorage.getItem('gs_token') || null;

export function setAuthToken(t){
  authToken = t;
  if(t) localStorage.setItem('gs_token', t); else localStorage.removeItem('gs_token');
}

export async function apiFetch(path, opts={}){
  const base = '/api';
  opts.headers = opts.headers || {};
  if(authToken) opts.headers['Authorization'] = `Bearer ${authToken}`;
  const res = await fetch(base + path, opts);
  if(!res.ok){
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}
const BASE_API = "http://localhost:8000"; // TODO: set via env in production

async function apiFetch(path, options = {}){
  try{
    const res = await fetch(BASE_API + path, options);
    if(!res.ok){
      const text = await res.text();
      throw new Error(`${res.status} ${res.statusText} - ${text}`);
    }
    return await res.json();
  }catch(err){
    console.error('API error', err);
    throw err;
  }
}

export { BASE_API, apiFetch };
