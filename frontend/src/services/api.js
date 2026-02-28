import axios from 'axios'

const base = import.meta.env.VITE_API_BASE_URL || ''

// backend routes are mounted at the root (e.g. http://localhost:8000/auth/...)
const api = axios.create({ baseURL: base })

// Request: attach token
api.interceptors.request.use((cfg)=>{
  const token = localStorage.getItem('gs_token')
  if(token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Response: global error handling
api.interceptors.response.use(
  res => res,
  err => {
    const status = err?.response?.status
    if(status === 401){
      localStorage.removeItem('gs_token')
      window.location.href = '/login'
      return Promise.reject(err)
    }
    if(status === 403){
      window.location.href = '/access-denied'
      return Promise.reject(err)
    }
    if(status >= 500){
      // minimal toast via alert for now; apps should show Snackbar
      alert('Server error. Please try again later.')
      return Promise.reject(err)
    }
    return Promise.reject(err)
  }
)

export default api
