import json
import time
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import sessionmaker
import os

class Base(DeclarativeBase):
    pass

class Simulation(Base):
    __tablename__ = "simulations"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[str] = mapped_column(unique=True)  # UUID para deduplicación
    monto: Mapped[float]
    tasa_anual: Mapped[float]
    plazo_meses: Mapped[int]
    tabla: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int]
    status: Mapped[str]
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

def calculate_amortization(monto, tasa_anual, plazo_meses):
    # Validación rápida
    if plazo_meses <= 0 or monto <= 0 or tasa_anual <= 0:
        return []
    
    tasa_mensual = tasa_anual / 12 / 100
    cuota = monto * (tasa_mensual / (1 - (1 + tasa_mensual) ** -plazo_meses))
    
    # Optimización: pre-allocate list
    tabla = [None] * plazo_meses
    saldo = monto
    
    for i in range(plazo_meses):
        interes = saldo * tasa_mensual
        abono = cuota - interes
        saldo -= abono
        tabla[i] = {
            "mes": i + 1,
            "cuota": round(cuota, 2),
            "interes": round(interes, 2),
            "abono": round(abono, 2),
            "saldo": round(max(0, saldo), 2)
        }
    return tabla

engine = create_engine(CONNECTION_STRING)
# Forzar refresh de metadata
Base.metadata.clear()
SessionLocal = sessionmaker(bind=engine)

def handler(event, context):
    db = SessionLocal()
    
    for record in event['Records']:
        body = json.loads(record['body'])
        
        # Mapear campos del mensaje
        request_id = body['request_id']
        monto = body['monto']
        
        # Buscar simulación existente
        sim = db.query(Simulation).filter_by(request_id=request_id).first()
        
        if not sim:
            print(f" Simulación no encontrada: {request_id}")
            continue
        
        # Solo auditoría con mock delay y fallos
        time.sleep(random.uniform(1, 3))
        
        try:
            if random.random() < 0.1:
                raise Exception("Fallo simulado en auditoría")
            
            # Auditoría exitosa
            log = AuditLog(
                simulation_id=sim.id,
                status="success",
                message=f"Auditoría procesada para monto {monto}"
            )
            db.add(log)
            db.commit()
            print(f" Auditoría procesada para simulación {sim.id}")
        except Exception as e:
            # Auditoría fallida
            log = AuditLog(
                simulation_id=sim.id,
                status="failed",
                message=str(e)
            )
            db.add(log)
            db.commit()
            print(f"Auditoría fallida: {str(e)}")
            # Re-lanzar para DLQ
            raise e
    
    db.close()
    return {'statusCode': 200}
