from sqlalchemy import Column, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(Integer, primary_key=True, index=True)
    monto = Column(Float)
    tasa_anual = Column(Float)
    plazo_meses = Column(Integer)
    tabla = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer)
    status = Column(Text)
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
