import React, { useContext } from 'react'
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material'
import AuthContext from '../context/AuthContext'

export default function Topbar(){
  const { user, logout } = useContext(AuthContext)
  return (
    <AppBar position="static" color="transparent" elevation={0} sx={{borderBottom:1, borderColor:'divider'}}>
      <Toolbar>
        <Typography variant="h6" sx={{flex:1}}>GramSight AI</Typography>
        {user ? <Box sx={{display:'flex',gap:2,alignItems:'center'}}>
          <Typography variant="body2">{user.email}</Typography>
          <Button onClick={logout} variant="outlined" size="small">Logout</Button>
        </Box> : <></>}
      </Toolbar>
    </AppBar>
  )
}
