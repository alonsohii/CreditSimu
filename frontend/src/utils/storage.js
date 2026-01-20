export const saveFormData = (monto, tasa, plazo) => {
  localStorage.setItem('lastMonto', monto);
  localStorage.setItem('lastTasa', tasa);
  localStorage.setItem('lastPlazo', plazo);
};

export const getFormData = () => {
  return {
    monto: localStorage.getItem('lastMonto') || '',
    tasa: localStorage.getItem('lastTasa') || '',
    plazo: localStorage.getItem('lastPlazo') || ''
  };
};
