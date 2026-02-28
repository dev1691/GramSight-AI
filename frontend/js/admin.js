import { apiFetch } from './api.js';

async function loadAdminDashboard(){
  try{
    const villages = await apiFetch('/admin/villages');
    const tbody = document.querySelector('#villageTable tbody');
    tbody.innerHTML = '';
    for(const v of villages){
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${v.id}</td><td>${v.name}</td><td>--</td>`;
      tbody.appendChild(tr);
    }
    document.getElementById('highRiskList').textContent = 'No high risk villages (mock)';
  }catch(err){
    console.error(err);
  }
}

window.addEventListener('load', loadAdminDashboard);
