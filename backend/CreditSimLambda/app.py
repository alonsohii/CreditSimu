import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column

# Models
class Base(DeclarativeBase):
    pass

class Simulation(Base):
    __tablename__ = "simulations"
    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[str] = mapped_column(unique=True)
    monto: Mapped[float]
    tasa_anual: Mapped[float]
    plazo_meses: Mapped[int]
    tabla: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

# DB Setup
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
engine = create_engine(CONNECTION_STRING) if CONNECTION_STRING else None
SessionLocal = sessionmaker(bind=engine) if engine else None

# Lazy imports - solo cuando se necesiten
def get_uuid():
    import uuid
    return str(uuid.uuid4())

def get_datetime():
    from datetime import datetime
    return datetime.utcnow().isoformat()

def get_boto3_client():
    import boto3
    return boto3.client(
        'sqs', 
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        config=boto3.session.Config(
            retries={'max_attempts': 1},
            max_pool_connections=50,
            parameter_validation=False,
            tcp_keepalive=True,
            connect_timeout=5,
            read_timeout=10
        )
    )

QUEUE_URL = os.getenv("QUEUE_URL")

# inicialización SQS
sqs = None

def get_sqs_client():
    global sqs
    if QUEUE_URL and sqs is None:
        try:
            sqs = get_boto3_client()
            # Warm-up
            sqs.get_queue_attributes(QueueUrl=QUEUE_URL, AttributeNames=['QueueArn'])
            print("SQS client initialized")
        except Exception as e:
            print(f"SQS init failed: {e}")
    return sqs

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def calculate_amortization(monto, tasa_anual, plazo_meses):
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

@app.options("/simulate")
def simulate_options():
    return {"message": "OK"}

@app.post("/simulate")
def simulate(request: dict):
    # Cálculo
    tabla = calculate_amortization(request["monto"], request["tasa_anual"], request["plazo_meses"])
    
    # Generar request_id
    request_id = get_uuid()
    
    # Guardar
    sim_id = None
    if SessionLocal:
        try:
            db = SessionLocal()
            sim = Simulation(
                request_id=request_id,
                monto=request["monto"],
                tasa_anual=request["tasa_anual"],
                plazo_meses=request["plazo_meses"],
                tabla=json.dumps(tabla)
            )
            db.add(sim)
            db.commit()

            sim_id = sim.id
            db.close()
            print(f"✅ Simulación guardada: {sim_id}")
        except Exception as e:
            print(f"❌ BD error: {e}")
            # Si BD falla, no enviar SQS
            return {"tabla_amortizacion": tabla, "error": "BD_ERROR"}
    
    # SQS mensaje mínimo - solo si BD fue exitosa
    if QUEUE_URL and sim_id:  
        try:
            sqs_client = get_sqs_client()
            if sqs_client:
                # Mensaje
                message = {
                    "request_id": request_id,
                    "monto": request["monto"],
                    "tasa_anual": request["tasa_anual"],
                    "plazo_meses": request["plazo_meses"],
                    "timestamp": get_datetime()
                }
                
                sqs_client.send_message(
                    QueueUrl=QUEUE_URL, 
                    MessageBody=json.dumps(message, separators=(',', ':'))
                )
        except Exception as e:
            print(f"SQS send failed: {e}")
    
    return {"tabla_amortizacion": tabla}

@app.get("/")
def root():
    return {"status": "CreditSim API running"}

@app.get("/warmup")
def warmup():
    get_sqs_client()  # Pre-warm SQS
    return {"warm": True}

def lambda_handler(event, context):
    # CloudWatch warming event
    if event.get('warmup'):
        print("Lambda warming")
        get_sqs_client()
        return {"statusCode": 200, "body": "warmed"}
    
    # Request normal via FastAPI
    mangum_handler = Mangum(app)
    return mangum_handler(event, context)

handler = lambda_handler