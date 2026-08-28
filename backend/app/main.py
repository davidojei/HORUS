from fastapi import FastAPI
from pydantic import BaseModel

from agents.horus.investigation_tools import investigate_transaction
from agents.horus.response_tools import determine_transaction_response
from agents.horus.response_executor import execute_response

app = FastAPI(
    title="HORUS",
    description="Enterprise Financial Security Operations Platform",
    version="1.0.0",
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