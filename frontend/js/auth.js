import { apiFetch, setAuthToken } from './api.js';

function saveToken(token){
  localStorage.setItem('gs_token', token);
  setAuthToken(token);
}

document.addEventListener('DOMContentLoaded', ()=>{
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  if(loginForm){
    loginForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const email = document.getElementById('email').value;
      const password = document.getElementById('password').value;
      try{
        const res = await apiFetch('/auth/login', {method:'POST', body: JSON.stringify({email, password}), headers:{'Content-Type':'application/json'}});
        saveToken(res.access_token);
        window.location.href = '../pages/dashboard.html';
      }catch(err){
        alert('Login failed');
      }
    })
  }

  if(registerForm){
    registerForm.addEventListener('submit', async (e)=>{
      e.preventDefault();
      const email = document.getElementById('r_email').value;
      const password = document.getElementById('r_password').value;
      try{
        const res = await apiFetch('/auth/register', {method:'POST', body: JSON.stringify({email, password}), headers:{'Content-Type':'application/json'}});
        saveToken(res.access_token);
        window.location.href = '../pages/dashboard.html';
      }catch(err){
        alert('Registration failed');
      }
    })
  }
});
