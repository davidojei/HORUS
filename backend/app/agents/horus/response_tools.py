from services.data_service import (
    get_transaction,
    get_account_transactions,
)

from detection.transaction_detector import detect_transaction
from detection.risk_engine import calculate_risk
from response_policy import determine_response


def determine_transaction_response(transaction_id: str) -> dict:
    """
    Determine the deterministic containment response for a transaction.

    IMPORTANT:
    This function ONLY determines what actions should happen.
    It does NOT execute those actions.
    """

    transaction = get_transaction(transaction_id)

    if not transaction:
        return {
            "success": False,
            "transaction_id": transaction_id,
            "error": f"Transaction {transaction_id} was not found.",
        }

    # 1. Detect anomalies
    detection_result = detect_transaction(transaction_id)

    if not detection_result.get("found"):
        return {
            "success": False,
            "transaction_id": transaction_id,
            "error": "Unable to determine fraud risk.",
        }

    # 2. Calculate deterministic risk
    risk_result = calculate_risk(detection_result)

    # 3. Get related transactions
    related_transactions = get_account_transactions(
        transaction["account_id"]
    )

    # 4. Determine deterministic response
    response = determine_response(
        risk_result=risk_result,
        transaction=transaction,
        related_transactions=related_transactions,
    )

    # 5. Reuse existing incident ID convention
    incident_id = f"INC-{transaction_id.split('-')[-1]}"

    # IMPORTANT:
    # No execution happens here.

    return {
        "success": True,
        "transaction_id": transaction_id,
        "account_id": transaction["account_id"],
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "signals": risk_result["signals"],
        "actions": response["actions"],
        "incident_id": incident_id,
        "execution_required": True,
    }