"""
HORUS Response Policy.

Determines which containment actions should be performed
based on deterministic fraud risk results.
"""


def determine_response(
    risk_result: dict,
    transaction: dict,
    related_transactions: list,
) -> dict:
    """
    Determine the appropriate response based on risk level.
    """

    risk_level = risk_result.get("risk_level")

    account_id = transaction["account_id"]
    device_id = transaction["device_id"]

    response = {
        "risk_level": risk_level,
        "actions": [],
    }

    if risk_level == "CRITICAL":

        response["actions"] = [
            {
                "action": "FREEZE_ACCOUNT",
                "account_id": account_id,
            },
            {
                "action": "REVOKE_DEVICE",
                "device_id": device_id,
            },
            {
                "action": "FLAG_TRANSACTIONS",
                "transaction_ids": [
                    tx["transaction_id"]
                    for tx in related_transactions
                    if tx["timestamp"] == transaction["timestamp"]
                ],
            },
            {
                "action": "CREATE_INCIDENT",
                "incident_type": "ACCOUNT_TAKEOVER",
                "severity": "CRITICAL",
                "account_id": account_id,
            },
        ]

    elif risk_level == "HIGH":

        response["actions"] = [
            {
                "action": "FLAG_TRANSACTIONS",
                "transaction_ids": [
                    transaction["transaction_id"]
                ],
            },
            {
                "action": "CREATE_INCIDENT",
                "incident_type": "SUSPICIOUS_TRANSACTION",
                "severity": "HIGH",
                "account_id": account_id,
            },
        ]

    elif risk_level == "MEDopIUM":

        response["actions"] = [
            {
                "action": "FLAG_TRANSACTIONS",
                "transaction_ids": [
                    transaction["transaction_id"]
                ],
            },
        ]

    else:
        response["actions"] = []

    return response