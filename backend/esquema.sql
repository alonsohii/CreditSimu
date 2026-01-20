-- Tabla de simulaciones
CREATE TABLE simulations (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID del request
    monto DECIMAL(12, 2) NOT NULL,
    tasa_anual DECIMAL(8, 4) NOT NULL,  -- Permite hasta 9999.9999%
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
CREATE INDEX idx_simulations_request_id ON simulations(request_id);
CREATE INDEX idx_audit_logs_simulation ON audit_logs(simulation_id);
