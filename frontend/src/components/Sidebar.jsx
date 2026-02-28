import React from 'react'
import { Drawer, List, ListItemButton, ListItemIcon, ListItemText, Toolbar } from '@mui/material'
import DashboardIcon from '@mui/icons-material/Dashboard'
import AccountTreeIcon from '@mui/icons-material/AccountTree'
import { Link as RouterLink } from 'react-router-dom'

export default function Sidebar(){
  return (
    <Drawer variant="permanent" open={true} sx={{width:240,['& .MuiDrawer-paper']: {width:240,boxSizing:'border-box'} }}>
      <Toolbar />
      <List>
        <ListItemButton component={RouterLink} to="/dashboard/farmer">
          <ListItemIcon><DashboardIcon/></ListItemIcon>
          <ListItemText primary="Farmer" />
        </ListItemButton>
        <ListItemButton component={RouterLink} to="/dashboard/admin">
          <ListItemIcon><AccountTreeIcon/></ListItemIcon>
          <ListItemText primary="Admin" />
        </ListItemButton>
      </List>
    </Drawer>
  )
}
