import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent


def get_incident(incident_id: str) -> dict | None:
    """
    Retrieve an incident by incident ID.
    """

    incidents_file = DATA_DIR / "incidents.json"

    if not incidents_file.exists():
        return None

    try:
        with open(incidents_file, "r", encoding="utf-8") as file:
            incidents = json.load(file)
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(incidents, list):
        return None

    for incident in incidents:
        if incident.get("incident_id") == incident_id:
            return incident

    return None


def get_incident_audit(incident_id: str) -> list:
    """
    Retrieve the complete audit trail for an incident.
    """

    audit_file = DATA_DIR.parent / "audit_log.json"

    if not audit_file.exists():
        return []

    try:
        with open(audit_file, "r", encoding="utf-8") as file:
            events = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(events, list):
        return []

    return [
        event
        for event in events
        if event.get("incident_id") == incident_id
    ]