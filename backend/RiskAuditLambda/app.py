import json
import time
import random
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
import os

class Base(DeclarativeBase):
    pass

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    simulation_id: Mapped[int]
    status: Mapped[str]
    message: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
engine = create_engine(CONNECTION_STRING)
Base.metadata.clear()
SessionLocal = sessionmaker(bind=engine)

def handler(event, context):
    db = SessionLocal()
    
    body = json.loads(event['Records'][0]['body'])
    
    # Mapear campos del mensaje
    simulation_id = body['simulation_id']
    monto = body['monto']
    
    # Solo auditoría con mock delay y fallos
    time.sleep(random.uniform(1, 3))
    
    try:
        if random.random() < 0.1:
            raise Exception("Fallo simulado en auditoría")
        
        # Auditoría exitosa
        log = AuditLog(
            simulation_id=simulation_id,
            status="success",
            message=f"Auditoría procesada para monto {monto}"
        )
        db.add(log)
        db.commit()
        print(f"✅ Auditoría procesada para simulación {simulation_id}")
    except Exception as e:
        # Auditoría fallida
        log = AuditLog(
            simulation_id=simulation_id,
            status="failed",
            message=str(e)
        )
        db.add(log)
        db.commit()
        print(f"❌ Auditoría fallida: {str(e)}")
        # Re-lanzar para DLQ
        raise e
    
    db.close()
    return {'statusCode': 200}