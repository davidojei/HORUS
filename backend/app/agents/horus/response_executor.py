from .action_tools import (
    freeze_account_tool,
    revoke_device_tool,
    flag_transaction_tool,
    create_incident_tool,
)

from services.audit_service import write_audit_event


def execute_response(
    response: dict,
    incident_id: str,
    transaction_id: str | None = None,
) -> dict:
    """
    Execute deterministic containment actions produced
    by the HORUS response policy.

    Every operational action is also recorded in the
    HORUS audit log.
    """

    results = []

    for action in response.get("actions", []):

        action_type = action.get("action")

        # --------------------------------------------------
        # FREEZE ACCOUNT
        # --------------------------------------------------

        if action_type == "FREEZE_ACCOUNT":

            target = action["account_id"]

            result = freeze_account_tool(
                account_id=target,
                incident_id=incident_id,
            )

            audit_status = (
                "SUCCESS"
                if result.get("success")
                else "FAILED"
            )

            write_audit_event(
                incident_id=incident_id,
                transaction_id=transaction_id,
                action=action_type,
                target=target,
                status=audit_status,
                result=result,
            )

        # --------------------------------------------------
        # REVOKE DEVICE
        # --------------------------------------------------

        elif action_type == "REVOKE_DEVICE":

            target = action["device_id"]

            result = revoke_device_tool(
                device_id=target,
                incident_id=incident_id,
            )

            audit_status = (
                "SUCCESS"
                if result.get("success")
                else "FAILED"
            )

            write_audit_event(
                incident_id=incident_id,
                transaction_id=transaction_id,
                action=action_type,
                target=target,
                status=audit_status,
                result=result,
            )

        # --------------------------------------------------
        # FLAG TRANSACTIONS
        # --------------------------------------------------

        elif action_type == "FLAG_TRANSACTIONS":

            transaction_results = []

            for transaction_id_to_flag in action["transaction_ids"]:

                result = flag_transaction_tool(
                    transaction_id=transaction_id_to_flag,
                    incident_id=incident_id,
                )

                transaction_results.append(result)

                audit_status = (
                    "SUCCESS"
                    if result.get("success")
                    else "FAILED"
                )

                write_audit_event(
                    incident_id=incident_id,
                    transaction_id=transaction_id_to_flag,
                    action="FLAG_TRANSACTION",
                    target=transaction_id_to_flag,
                    status=audit_status,
                    result=result,
                )

            result = {
                "action": "FLAG_TRANSACTIONS",
                "results": transaction_results,
            }

        # --------------------------------------------------
        # CREATE INCIDENT
        # --------------------------------------------------

        elif action_type == "CREATE_INCIDENT":

            target = incident_id

            result = create_incident_tool(
                incident_id=incident_id,
                incident_type=action["incident_type"],
                severity=action["severity"],
                account_id=action["account_id"],
                summary=(
                    "Automated HORUS incident response for "
                    f"{action['incident_type']}."
                ),
            )

            audit_status = (
                "SUCCESS"
                if result.get("success")
                else "FAILED"
            )

            write_audit_event(
                incident_id=incident_id,
                transaction_id=transaction_id,
                action=action_type,
                target=target,
                status=audit_status,
                result=result,
            )

        # --------------------------------------------------
        # UNKNOWN ACTION
        # --------------------------------------------------

        else:

            result = {
                "success": False,
                "action": action_type,
                "error": "Unknown response action.",
            }

            write_audit_event(
                incident_id=incident_id,
                transaction_id=transaction_id,
                action=str(action_type),
                target="UNKNOWN",
                status="FAILED",
                result=result,
            )

        results.append(result)

    return {
        "success": all(
            result.get("success", True)
            for result in results
        ),
        "risk_level": response.get("risk_level"),
        "incident_id": incident_id,
        "results": results,
    }