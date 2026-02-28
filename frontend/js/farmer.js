import { apiFetch } from './api.js';

const villageId = 1; // TODO: wire real auth and selection

async function loadFarmerDashboard(){
  try{
    const risk = await apiFetch(`/farmer/${villageId}/risk`);
    const weather = await apiFetch(`/farmer/${villageId}/weather`);
    const market = await apiFetch(`/farmer/${villageId}/market`);

    const score = risk?.risk?.score ?? '--';
    const category = risk?.risk?.category ?? 'unknown';
    const $risk = document.getElementById('riskScore');
    $risk.textContent = score;
    $risk.className = `risk-score risk-${category}`;
    document.getElementById('riskExplanation').textContent = risk?.explanation ?? '';

    document.getElementById('weatherData').textContent = JSON.stringify(weather.weather);
    document.getElementById('marketData').textContent = JSON.stringify(market.markets);
    document.getElementById('advisoryText').textContent = 'Advisory: ' + (risk?.explanation ?? 'No advisory yet');
  }catch(err){
    console.error(err);
  }
}

window.addEventListener('load', loadFarmerDashboard);
