from .action_tools import (
    freeze_account_tool,
    revoke_device_tool,
    flag_transaction_tool,
    create_incident_tool,
)


def execute_response(
    response: dict,
    incident_id: str,
) -> dict:
    """
    Execute deterministic containment actions produced
    by the HORUS response policy.
    """

    results = []

    for action in response.get("actions", []):

        action_type = action.get("action")

        if action_type == "FREEZE_ACCOUNT":

            result = freeze_account_tool(
                account_id=action["account_id"],
                incident_id=incident_id,
            )

        elif action_type == "REVOKE_DEVICE":

            result = revoke_device_tool(
                device_id=action["device_id"],
                incident_id=incident_id,
            )

        elif action_type == "FLAG_TRANSACTIONS":

            transaction_results = []

            for transaction_id in action["transaction_ids"]:

                result = flag_transaction_tool(
                    transaction_id=transaction_id,
                    incident_id=incident_id,
                )

                transaction_results.append(result)

            result = {
                "action": "FLAG_TRANSACTIONS",
                "results": transaction_results,
            }

        elif action_type == "CREATE_INCIDENT":

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

        else:

            result = {
                "success": False,
                "action": action_type,
                "error": "Unknown response action.",
            }

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