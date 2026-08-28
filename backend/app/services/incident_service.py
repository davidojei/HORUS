import json
from pathlib import Path


INCIDENTS_PATH = (
    Path(__file__).resolve().parent.parent / "services" / "incidents.json"
)


def get_incident(incident_id: str) -> dict | None:
    """
    Retrieve a persisted HORUS incident by incident ID.
    """

    if not INCIDENTS_PATH.exists():
        return None

    try:
        with open(INCIDENTS_PATH, "r", encoding="utf-8") as file:
            incidents = json.load(file)
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(incidents, list):
        return None

    for incident in incidents:
        if incident.get("incident_id") == incident_id:
            return incident

    return None