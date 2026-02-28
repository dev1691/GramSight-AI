import React, { useEffect, useState } from 'react'
import { Box, Grid, Card, CardContent, Typography, LinearProgress } from '@mui/material'
import api from '../services/api'
import { Chart } from 'react-chartjs-2'

export default function FarmerDashboard(){
  const [summary, setSummary] = useState(null)

  useEffect(()=>{
    let mounted = true
    api.get('/farmer/dashboard').then(r=>{ if(mounted) setSummary(r.data) }).catch(()=>{})
    return ()=>{ mounted = false }
  },[])

  return (
    <Box sx={{p:3}}>
      <Typography variant="h4" mb={2}>Farmer Dashboard</Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6} lg={4}>
          <Card elevation={3}><CardContent>
            <Typography variant="h6">Risk Indicator</Typography>
            <Typography variant="h3">{summary?.risk_score ?? '--'}</Typography>
            <LinearProgress variant="determinate" value={summary?.risk_score ?? 0} sx={{mt:2}} />
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={6} lg={8}>
          <Card elevation={3}><CardContent>
            <Typography variant="h6">Rainfall (last 12 months)</Typography>
            <div style={{height:220}}>Chart placeholder</div>
          </CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  )
}
