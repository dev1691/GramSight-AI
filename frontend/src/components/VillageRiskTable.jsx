import React, { useState } from 'react';
import {
  Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TableSortLabel, Chip, Box,
} from '@mui/material';
import { getRiskColor, getRiskLabel } from '../theme/theme';

const DEMO_VILLAGES = [
  { id: 1, name: 'Rajpur', district: 'Pune', score: 72, crop: 'Rice' },
  { id: 2, name: 'Devgad', district: 'Sindhudurg', score: 45, crop: 'Mango' },
  { id: 3, name: 'Malshiras', district: 'Solapur', score: 83, crop: 'Sugarcane' },
  { id: 4, name: 'Kothrud', district: 'Pune', score: 28, crop: 'Wheat' },
  { id: 5, name: 'Sinhagad', district: 'Pune', score: 56, crop: 'Soybean' },
  { id: 6, name: 'Baramati', district: 'Pune', score: 91, crop: 'Sugarcane' },
  { id: 7, name: 'Pandharpur', district: 'Solapur', score: 67, crop: 'Jowar' },
  { id: 8, name: 'Wai', district: 'Satara', score: 34, crop: 'Strawberry' },
];

const COLUMNS = [
  { id: 'name', label: 'Village', align: 'left' },
  { id: 'district', label: 'District', align: 'left' },
  { id: 'crop', label: 'Primary Crop', align: 'left' },
  { id: 'score', label: 'Risk Score', align: 'right' },
  { id: 'status', label: 'Status', align: 'center' },
];

export default function VillageRiskTable({ villages = DEMO_VILLAGES, onSelect }) {
  const [orderBy, setOrderBy] = useState('score');
  const [order, setOrder] = useState('desc');

  const handleSort = (field) => {
    if (field === 'status') return;
    setOrder(orderBy === field && order === 'desc' ? 'asc' : 'desc');
    setOrderBy(field);
  };

  const sorted = [...villages].sort((a, b) => {
    const valA = a[orderBy];
    const valB = b[orderBy];
    const cmp = valA < valB ? -1 : valA > valB ? 1 : 0;
    return order === 'asc' ? cmp : -cmp;
  });

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
        <Typography variant="h6" sx={{ mb: 2 }}>Village Risk Overview</Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                {COLUMNS.map((col) => (
                  <TableCell
                    key={col.id}
                    align={col.align}
                    sx={{ fontWeight: 600, color: 'text.secondary', fontSize: 12, borderBottom: '2px solid', borderColor: 'divider' }}
                  >
                    {col.id !== 'status' ? (
                      <TableSortLabel
                        active={orderBy === col.id}
                        direction={orderBy === col.id ? order : 'asc'}
                        onClick={() => handleSort(col.id)}
                      >
                        {col.label}
                      </TableSortLabel>
                    ) : col.label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sorted.map((v) => {
                const color = getRiskColor(v.score);
                return (
                  <TableRow
                    key={v.id}
                    hover
                    onClick={() => onSelect?.(v)}
                    sx={{
                      cursor: onSelect ? 'pointer' : 'default',
                      '&:last-child td': { borderBottom: 0 },
                      transition: 'background 0.1s ease',
                    }}
                  >
                    <TableCell sx={{ fontWeight: 600, fontSize: 13 }}>{v.name}</TableCell>
                    <TableCell sx={{ fontSize: 13, color: 'text.secondary' }}>{v.district}</TableCell>
                    <TableCell sx={{ fontSize: 13 }}>{v.crop}</TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                        <Box
                          sx={{
                            width: 36,
                            height: 6,
                            borderRadius: 3,
                            bgcolor: 'rgba(0,0,0,0.06)',
                            overflow: 'hidden',
                          }}
                        >
                          <Box
                            sx={{
                              width: `${v.score}%`,
                              height: '100%',
                              bgcolor: color,
                              borderRadius: 3,
                            }}
                          />
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 700, color, minWidth: 24, textAlign: 'right' }}>
                          {v.score}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={getRiskLabel(v.score)}
                        size="small"
                        sx={{
                          height: 24,
                          fontSize: '0.7rem',
                          fontWeight: 600,
                          bgcolor: `${color}15`,
                          color,
                        }}
                      />
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}
