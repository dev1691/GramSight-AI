import React, { useState } from 'react'
import { Box, Paper, TextField, Button, Typography } from '@mui/material'
import api from '../services/api'
import { useNavigate } from 'react-router-dom'

export default function Register(){
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const navigate = useNavigate()

  const onSubmit = async (e)=>{
    e.preventDefault()
    try{
      const res = await api.post('/auth/register', { email, password })
      const token = res.data.access_token
      localStorage.setItem('gs_token', token)
      navigate('/dashboard/farmer')
    }catch(err){
      alert('Registration failed')
    }
  }

  return (
    <Box sx={{display:'flex',justifyContent:'center',alignItems:'center',height:'80vh'}}>
      <Paper sx={{p:4,width:420}} elevation={6}>
        <Typography variant="h5" mb={2}>Create account</Typography>
        <form onSubmit={onSubmit}>
          <TextField label="Email" fullWidth margin="normal" value={email} onChange={e=>setEmail(e.target.value)} />
          <TextField label="Password" type="password" fullWidth margin="normal" value={password} onChange={e=>setPassword(e.target.value)} />
          <Button type="submit" variant="contained" color="primary" sx={{mt:2}}>Register</Button>
        </form>
      </Paper>
    </Box>
  )
}
