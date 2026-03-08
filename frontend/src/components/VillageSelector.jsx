import React from 'react';
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material';

const DEMO_VILLAGES = [
  { id: 1, name: 'Rajpur' },
  { id: 2, name: 'Devgad' },
  { id: 3, name: 'Malshiras' },
  { id: 4, name: 'Kothrud' },
  { id: 5, name: 'Sinhagad' },
  { id: 6, name: 'Baramati' },
  { id: 7, name: 'Pandharpur' },
  { id: 8, name: 'Wai' },
];

export default function VillageSelector({ value, onChange, villages = DEMO_VILLAGES, size = 'small' }) {
  return (
    <FormControl size={size} sx={{ minWidth: 180 }}>
      <InputLabel>Select Village</InputLabel>
      <Select
        value={value}
        label="Select Village"
        onChange={(e) => onChange(e.target.value)}
      >
        {villages.map((v) => (
          <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
