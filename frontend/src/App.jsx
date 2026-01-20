import React, { useState } from 'react';
import { Container, Typography, Box } from '@mui/material';
import Form from './components/Form';
import Table from './components/Table';

function App() {
  const [tabla, setTabla] = useState([]);

  const [loading, setLoading] = useState(false);

  const handleSimulate = async (data) => {
    setLoading(true);
    try {
      const response = await fetch('https://fcxi5ssg63.execute-api.us-east-1.amazonaws.com/prod/simulate', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'x-api-key': 'C2IZk27QHL21lzi6OYgLI15trkyDwqEHCdIXrMZf'
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      setTabla(result.tabla_amortizacion);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = () => {
    setTabla([]);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ fontWeight: 700, color: '#1f2937' }}>
           CreditSim - Simulador de Crédito
        </Typography>
        <Form onSubmit={handleSimulate} loading={loading} onFormChange={handleFormChange} />
        <Table data={tabla} />
      </Box>
    </Container>
  );
}

export default App;
