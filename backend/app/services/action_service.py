from datetime import datetime
from pathlib import Path
import json


# ---------------------------------------------------------
# Enterprise Action State
# ---------------------------------------------------------

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "enterprise"

ACCOUNTS_FILE = DATA_DIR / "accounts.json"
DEVICES_FILE = DATA_DIR / "devices.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

AUDIT_FILE = DATA_DIR / "audit_log.json"


def _load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _audit(action, target_type, target_id, incident_id, details=None):
    """
    Record every enterprise action performed by Horus.
    """

    try:
        audit_log = _load(AUDIT_FILE)
    except FileNotFoundError:
        audit_log = []

    event = {
        "event_id": f"AUDIT-{len(audit_log) + 1:06d}",
        "timestamp": datetime.utcnow().isoformat(),
        "agent": "horus",
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "incident_id": incident_id,
        "details": details or {},
    }

    audit_log.append(event)
    _save(AUDIT_FILE, audit_log)

    return event


# ---------------------------------------------------------
# ACCOUNT ACTIONS
# ---------------------------------------------------------

def freeze_account(account_id: str, incident_id: str):
    """
    Freeze an account to prevent further transactions.
    """

    accounts = _load(ACCOUNTS_FILE)

    for account in accounts:
        if account["account_id"] == account_id:

            previous_status = account["status"]
            account["status"] = "FROZEN"

            _save(ACCOUNTS_FILE, accounts)

            audit = _audit(
                action="FREEZE_ACCOUNT",
                target_type="ACCOUNT",
                target_id=account_id,
                incident_id=incident_id,
                details={
                    "previous_status": previous_status,
                    "new_status": "FROZEN",
                },
            )

            return {
                "success": True,
                "action": "FREEZE_ACCOUNT",
                "account_id": account_id,
                "status": "FROZEN",
                "audit_event": audit,
            }

    return {
        "success": False,
        "error": f"Account {account_id} not found",
    }


# ---------------------------------------------------------
# DEVICE ACTIONS
# ---------------------------------------------------------

def revoke_device(device_id: str, incident_id: str):
    """
    Revoke trust from a device.
    """

    devices = _load(DEVICES_FILE)

    for device in devices:
        if device["device_id"] == device_id:

            device["trusted"] = False
            device["revoked"] = True
            device["revoked_at"] = datetime.utcnow().isoformat()

            _save(DEVICES_FILE, devices)

            audit = _audit(
                action="REVOKE_DEVICE",
                target_type="DEVICE",
                target_id=device_id,
                incident_id=incident_id,
            )

            return {
                "success": True,
                "action": "REVOKE_DEVICE",
                "device_id": device_id,
                "revoked": True,
                "audit_event": audit,
            }

    return {
        "success": False,
        "error": f"Device {device_id} not found",
    }


# ---------------------------------------------------------
# TRANSACTION ACTIONS
# ---------------------------------------------------------

def flag_transaction(transaction_id: str, incident_id: str):
    """
    Flag a transaction for fraud review/reversal.
    """

    transactions = _load(TRANSACTIONS_FILE)

    for transaction in transactions:
        if transaction["transaction_id"] == transaction_id:

            transaction["fraud_flag"] = True
            transaction["incident_id"] = incident_id
            transaction["flagged_at"] = datetime.utcnow().isoformat()

            _save(TRANSACTIONS_FILE, transactions)

            audit = _audit(
                action="FLAG_TRANSACTION",
                target_type="TRANSACTION",
                target_id=transaction_id,
                incident_id=incident_id,
            )

            return {
                "success": True,
                "action": "FLAG_TRANSACTION",
                "transaction_id": transaction_id,
                "fraud_flag": True,
                "audit_event": audit,
            }

    return {
        "success": False,
        "error": f"Transaction {transaction_id} not found",
    }


# ---------------------------------------------------------
# INCIDENT ACTION
# ---------------------------------------------------------

def create_incident(
    incident_id: str,
    incident_type: str,
    severity: str,
    account_id: str,
    summary: str,
):
    """
    Create a persistent enterprise incident record.
    """

    incidents_file = DATA_DIR / "incidents.json"

    try:
        incidents = _load(incidents_file)
    except FileNotFoundError:
        incidents = []

    incident = {
        "incident_id": incident_id,
        "type": incident_type,
        "severity": severity,
        "account_id": account_id,
        "summary": summary,
        "status": "OPEN",
        "created_at": datetime.utcnow().isoformat(),
    }

    incidents.append(incident)

    _save(incidents_file, incidents)

    audit = _audit(
        action="CREATE_INCIDENT",
        target_type="INCIDENT",
        target_id=incident_id,
        incident_id=incident_id,
        details={
            "severity": severity,
            "type": incident_type,
        },
    )

    return {
        "success": True,
        "incident": incident,
        "audit_event": audit,
    }