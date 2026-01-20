import React, { useState, useEffect } from 'react';
import { TextField, Button, Paper, Grid, InputAdornment } from '@mui/material';
import { AttachMoney, Percent, CalendarMonth, Calculate } from '@mui/icons-material';
import { saveFormData, getFormData } from '../utils/storage';

function Form({ onSubmit, loading, onFormChange }) {
  const savedData = getFormData();
  const [monto, setMonto] = useState(savedData.monto);
  const [tasa, setTasa] = useState(savedData.tasa);
  const [plazo, setPlazo] = useState(savedData.plazo);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  useEffect(() => {
    saveFormData(monto, tasa, plazo);
    // Solo limpiar tabla después de la carga inicial
    if (!isInitialLoad && onFormChange) {
      onFormChange();
    }
    if (isInitialLoad) {
      setIsInitialLoad(false);
    }
  }, [monto, tasa, plazo]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSubmit({
      monto: parseFloat(monto),
      tasa_anual: parseFloat(tasa),
      plazo_meses: parseInt(plazo)
    });
  };

  return (
    <Paper elevation={3} style={{ padding: '30px', marginBottom: '30px' }}>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Monto del Crédito"
              type="number"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <AttachMoney />
                  </InputAdornment>
                ),
              }}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Tasa Anual"
              type="number"
              value={tasa}
              onChange={(e) => setTasa(e.target.value)}
              required
              inputProps={{ step: "0.01" }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Percent />
                  </InputAdornment>
                ),
              }}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Plazo (meses)"
              type="number"
              value={plazo}
              onChange={(e) => setPlazo(e.target.value)}
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <CalendarMonth />
                  </InputAdornment>
                ),
              }}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              disabled={loading}
              startIcon={<Calculate />}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                padding: '12px',
                fontSize: '16px'
              }}
            >
              {loading ? 'Calculando...' : 'Calcular Amortización'}
            </Button>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
}

export default Form;
