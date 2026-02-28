import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import FarmerDashboard from './pages/FarmerDashboard'
import AdminDashboard from './pages/AdminDashboard'
import ProtectedRoute from './components/ProtectedRoute'
import Topbar from './components/Topbar'
import Sidebar from './components/Sidebar'

export default function App(){
  return (
    <div style={{display:'flex', minHeight:'100vh'}}>
      <Sidebar />
      <div style={{flex:1}}>
        <Topbar />
        <Routes>
          <Route path='/' element={<Navigate to='/dashboard/farmer' replace />} />
          <Route path='/login' element={<Login/>} />
          <Route path='/register' element={<Register/>} />

          <Route path='/dashboard/farmer' element={<ProtectedRoute allowedRoles={["farmer"]}><FarmerDashboard/></ProtectedRoute>} />
          <Route path='/dashboard/admin' element={<ProtectedRoute allowedRoles={["admin"]}><AdminDashboard/></ProtectedRoute>} />
        </Routes>
      </div>
    </div>
  )
}
