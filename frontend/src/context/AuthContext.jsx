import React, { createContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext(null)

function decodeToken(token){
  try{
    const payload = token.split('.')[1]
    const json = atob(payload.replace(/-/g,'+').replace(/_/g,'/'))
    return JSON.parse(json)
  }catch(e){return null}
}

export const AuthProvider = ({children})=>{
  const [token, setToken] = useState(localStorage.getItem('gs_token'))
  const [user, setUser] = useState(null)

  useEffect(()=>{
    if(token){
      localStorage.setItem('gs_token', token)
      const decoded = decodeToken(token)
      setUser(decoded)
    }else{
      localStorage.removeItem('gs_token')
      setUser(null)
    }
  },[token])

  const login = async (email, password)=>{
    const res = await api.post('/auth/login', { email, password })
    setToken(res.data.access_token)
    return res
  }

  const logout = ()=>{
    setToken(null)
  }

  return <AuthContext.Provider value={{user, token, login, logout}}>{children}</AuthContext.Provider>
}

export default AuthContext
