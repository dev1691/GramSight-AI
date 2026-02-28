import { apiFetch } from './api.js';

function renderForRole(role){
  const container = document.getElementById('dashboardRoot');
  if(!container) return;
  if(role === 'admin'){
    container.innerHTML = `<h2>Admin Dashboard</h2><p>Admin metrics will appear here.</p>`;
  }else{
    container.innerHTML = `<h2>Farmer Dashboard</h2><p>Farmer-specific summaries will appear here.</p>`;
  }
}

document.addEventListener('DOMContentLoaded', async ()=>{
  const token = localStorage.getItem('gs_token');
  if(!token) { window.location.href = '../pages/login.html'; return; }
  try{
    const data = await apiFetch('/auth/me');
    renderForRole(data.role);
  }catch(err){
    console.error(err);
    window.location.href = '../pages/login.html';
  }
});
