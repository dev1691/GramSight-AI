import React from 'react';
import {
  Card, CardContent, Typography, Box, List, ListItem,
  ListItemText, Chip, Divider, Avatar,
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import { getRiskColor } from '../theme/theme';

const DEMO_ALERTS = [
  { id: 6, name: 'Baramati', score: 91, reason: 'Severe drought conditions + market price crash' },
  { id: 3, name: 'Malshiras', score: 83, reason: 'Critically low soil moisture, extreme heat' },
  { id: 1, name: 'Rajpur', score: 72, reason: 'Declining rainfall, rising crop stress index' },
];

export default function HighRiskAlerts({ alerts = DEMO_ALERTS }) {
  if (alerts.length === 0) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 200 }}>
          <Box sx={{ width: 48, height: 48, borderRadius: '50%', bgcolor: 'rgba(76,175,80,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
            <WarningAmberIcon sx={{ color: '#4CAF50' }} />
          </Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 0.5 }}>All Clear</Typography>
          <Typography variant="body2" color="text.secondary">No high-risk villages detected.</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ height: '100%', border: '1px solid', borderColor: 'rgba(244,67,54,0.2)' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <WarningAmberIcon sx={{ color: '#D32F2F' }} />
          <Typography variant="h6" sx={{ flex: 1 }}>High Risk Alerts</Typography>
          <Chip
            label={`${alerts.length} villages`}
            size="small"
            color="error"
            sx={{ fontWeight: 700 }}
          />
        </Box>

        <List disablePadding>
          {alerts.map((alert, i) => {
            const color = getRiskColor(alert.score);
            return (
              <React.Fragment key={alert.id}>
                {i > 0 && <Divider sx={{ my: 0.5 }} />}
                <ListItem
                  sx={{
                    px: 1.5, py: 1.5, borderRadius: 2,
                    '&:hover': { bgcolor: 'rgba(244,67,54,0.03)' },
                    transition: 'background 0.15s ease',
                  }}
                >
                  <Avatar
                    sx={{
                      width: 36, height: 36, mr: 2,
                      bgcolor: `${color}15`, color,
                      fontSize: 13, fontWeight: 800,
                    }}
                  >
                    {alert.score}
                  </Avatar>
                  <ListItemText
                    primary={alert.name}
                    secondary={alert.reason}
                    primaryTypographyProps={{ fontWeight: 600, fontSize: 14 }}
                    secondaryTypographyProps={{ fontSize: 12, mt: 0.3 }}
                  />
                </ListItem>
              </React.Fragment>
            );
          })}
        </List>
      </CardContent>
    </Card>
  );
}
