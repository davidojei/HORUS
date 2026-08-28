import json
from datetime import datetime, timezone
from pathlib import Path


AUDIT_LOG_PATH = Path(__file__).resolve().parent.parent / "audit_log.json"


def write_audit_event(
    *,
    incident_id: str,
    transaction_id: str | None,
    action: str,
    target: str,
    status: str,
    result: dict,
) -> dict:
    """
    Persist one immutable HORUS operational audit event.
    """

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "incident_id": incident_id,
        "transaction_id": transaction_id,
        "action": action,
        "target": target,
        "status": status,
        "result": result,
    }

    existing_events = []

    if AUDIT_LOG_PATH.exists():
        try:
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as file:
                existing_events = json.load(file)

            if not isinstance(existing_events, list):
                existing_events = []

        except (json.JSONDecodeError, OSError):
            existing_events = []

    existing_events.append(event)

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as file:
        json.dump(
            existing_events,
            file,
            indent=4,
        )

    return event