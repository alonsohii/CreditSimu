-- Tabla de simulaciones
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    monto DECIMAL(12, 2) NOT NULL,
    tasa_anual DECIMAL(8, 4) NOT NULL,  
    plazo_meses INTEGER NOT NULL,
    tabla TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de logs de auditoría
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER REFERENCES simulations(id),
    status VARCHAR(20) NOT NULL,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_simulations_created ON simulations(created_at);
CREATE INDEX idx_audit_logs_simulation ON audit_logs(simulation_id);
