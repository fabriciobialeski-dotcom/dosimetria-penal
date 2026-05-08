
from fastapi import FastAPI
from pydantic import BaseModel
import uuid
import json
import os

app = FastAPI()

DB_FILE = "db.json"

class Calculo(BaseModel):
    dados: dict

def carregar_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def salvar_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

@app.post("/calculos")
def criar_calculo(calculo: Calculo):
    db = carregar_db()

    calc_id = str(uuid.uuid4())[:8]

    db[calc_id] = calculo.dados

    salvar_db(db)

    return {"id": calc_id}

@app.get("/calculos/{calc_id}")
def obter_calculo(calc_id: str):
    db = carregar_db()

    if calc_id not in db:
        return {"erro": "não encontrado"}

    return {"dados": db[calc_id]}
