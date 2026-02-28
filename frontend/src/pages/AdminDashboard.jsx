import React, { useEffect, useState } from 'react'
import { Box, Grid, Card, CardContent, Typography } from '@mui/material'
import api from '../services/api'

export default function AdminDashboard(){
  const [kpis, setKpis] = useState(null)

  useEffect(()=>{
    let mounted = true
    api.get('/admin/dashboard').then(r=>{ if(mounted) setKpis(r.data) }).catch(()=>{})
    return ()=>{ mounted = false }
  },[])

  return (
    <Box sx={{p:3}}>
      <Typography variant="h4" mb={2}>Admin Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Card elevation={3}><CardContent>
            <Typography variant="h6">Total Villages</Typography>
            <Typography variant="h3">{kpis?.total_villages ?? '--'}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={3}><CardContent>
            <Typography variant="h6">Total Farmers</Typography>
            <Typography variant="h3">{kpis?.total_farmers ?? '--'}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={3}><CardContent>
            <Typography variant="h6">High-risk Villages</Typography>
            <Typography variant="h3">{kpis?.high_risk ?? '--'}</Typography>
          </CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  )
}
