import React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Paper } from '@mui/material';

function Table({ data }) {
  if (!data || data.length === 0) return null;

  const columns = [
    { field: 'mes', headerName: 'Mes', width: 100 },
    { field: 'cuota', headerName: 'Cuota', width: 150, valueFormatter: (params) => `$${params.value.toLocaleString('es-MX', {minimumFractionDigits: 2})}` },
    { field: 'interes', headerName: 'Interés', width: 150, valueFormatter: (params) => `$${params.value.toLocaleString('es-MX', {minimumFractionDigits: 2})}` },
    { field: 'abono', headerName: 'Abono Capital', width: 150, valueFormatter: (params) => `$${params.value.toLocaleString('es-MX', {minimumFractionDigits: 2})}` },
    { field: 'saldo', headerName: 'Saldo', width: 150, valueFormatter: (params) => `$${params.value.toLocaleString('es-MX', {minimumFractionDigits: 2})}` },
  ];

  const rows = data.map((row) => ({ id: row.mes, ...row }));

  return (
    <Paper elevation={3} style={{ height: 500, width: '100%', marginTop: 20 }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={10}
        rowsPerPageOptions={[10, 25, 50]}
        disableSelectionOnClick
      />
    </Paper>
  );
}

export default Table;
