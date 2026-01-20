import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import boto3
from mangum import Mangum
from models import Simulation

CONNECTION_STRING = os.getenv("CONNECTION_STRING")
QUEUE_URL = os.getenv("QUEUE_URL")

engine = create_engine(CONNECTION_STRING)
SessionLocal = sessionmaker(bind=engine)
sqs = boto3.client('sqs', region_name=os.getenv('AWS_REGION', 'us-east-1'))

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class SimulationRequest(BaseModel):
    monto: float
    tasa_anual: float
    plazo_meses: int

# Función para calcular la tabla de amortización   
def calculate_amortization(monto, tasa_anual, plazo_meses):
    tasa_mensual = tasa_anual / 12 / 100
    cuota = monto * (tasa_mensual / (1 - (1 + tasa_mensual) ** -plazo_meses))
    tabla = []
    saldo = monto
    for i in range(1, plazo_meses + 1):
        interes = saldo * tasa_mensual
        abono = cuota - interes
        saldo -= abono
        tabla.append({
            "mes": i,
            "cuota": round(cuota, 2),
            "interes": round(interes, 2),
            "abono": round(abono, 2),
            "saldo": round(max(0, saldo), 2)
        })
    return tabla

# Endpoint para crear simulación y enviar mensaje a SQS   
@app.post("/simulate")
def simulate(request: SimulationRequest):
    tabla = calculate_amortization(request.monto, request.tasa_anual, request.plazo_meses)
    
    db = SessionLocal()
    sim = Simulation(
        monto=request.monto,
        tasa_anual=request.tasa_anual,
        plazo_meses=request.plazo_meses,
        tabla=json.dumps(tabla)
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)

    sim_id = sim.id
    db.close()
    
    message = {
        "simulation_id": sim_id,
        "monto": request.monto,
        "tasa_anual": request.tasa_anual,
        "plazo_meses": request.plazo_meses,
        "timestamp": datetime.utcnow().isoformat()
    }
    sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(message))
    
    return {"tabla_amortizacion": tabla}

@app.get("/")
def root():
    return {"status": "CreditSim API running"}

handler = Mangum(app)
