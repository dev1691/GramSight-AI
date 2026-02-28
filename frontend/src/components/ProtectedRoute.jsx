import React, { useContext } from 'react'
import { Navigate } from 'react-router-dom'
import AuthContext from '../context/AuthContext'

export default function ProtectedRoute({ children, allowedRoles=[] }){
  const { user } = useContext(AuthContext)
  if(!user) return <Navigate to="/login" replace />
  if(allowedRoles.length && !allowedRoles.includes(user.role)) return <Navigate to="/access-denied" replace />
  return children
}
