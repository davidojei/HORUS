from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.data_service import get_transaction
from services.incident_api import (
    get_incident,
    get_incident_audit,
)

from agents.horus.investigation_tools import investigate_transaction
from agents.horus.response_tools import determine_transaction_response
from agents.horus.response_executor import execute_response

app = FastAPI(
    title="HORUS",
    description="Enterprise Financial Security Operations Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "service": "HORUS",
        "status": "online",
        "version": "1.0.0",
    }

class TransactionRequest(BaseModel):
    transaction_id: str


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "HORUS",
    }


@app.get("/incidents/{incident_id}")
def incident(incident_id: str):

    result = get_incident(incident_id)

    if not result:
        return {
            "success": False,
            "incident_id": incident_id,
            "error": "Incident not found.",
        }

    return {
        "success": True,
        "incident": result,
    }


@app.get("/incidents/{incident_id}/audit")
def incident_audit(incident_id: str):

    result = get_incident_audit(incident_id)

    return {
        "success": True,
        "incident_id": incident_id,
        "count": len(result),
        "events": result,
    }


@app.get("/transactions/{transaction_id}")
def transaction(transaction_id: str):

    result = get_transaction(transaction_id)

    if not result:
        return {
            "success": False,
            "transaction_id": transaction_id,
            "error": "Transaction not found.",
        }

    return {
        "success": True,
        "transaction": result,
    }


@app.post("/investigate")
def investigate(request: TransactionRequest):
    return investigate_transaction(request.transaction_id)


@app.post("/respond")
def respond(request: TransactionRequest):
    return determine_transaction_response(request.transaction_id)

@app.post("/execute")
def execute(request: TransactionRequest):

    response = determine_transaction_response(
        request.transaction_id
    )

    if not response.get("success"):
        return response

    execution = execute_response(
        response=response,
	incident_id=response["incident_id"],
        transaction_id=request.transaction_id,
    )

    return {
        "success": execution["success"],
        "transaction_id": request.transaction_id,
        "risk_level": response["risk_level"],
        "risk_score": response["risk_score"],
        "signals": response["signals"],
        "actions": response["actions"],
        "incident_id": response["incident_id"],
        "execution": execution,
    }