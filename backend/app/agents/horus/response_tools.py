from services.data_service import (
    get_transaction,
    get_account_transactions,
)
from detection.transaction_detector import detect_transaction
from detection.risk_engine import calculate_risk
from response_policy import determine_response


def determine_transaction_response(transaction_id: str) -> dict:
    """
    Determine the appropriate containment response for a transaction.

    The response is determined by HORUS's deterministic fraud detection
    and response policy engines.

    This tool does NOT execute any actions.
    It only returns the policy-approved action plan.
    """

    transaction = get_transaction(transaction_id)

    if not transaction:
        return {
            "success": False,
            "transaction_id": transaction_id,
            "error": f"Transaction {transaction_id} was not found.",
        }

    detection_result = detect_transaction(transaction_id)

    if not detection_result.get("found"):
        return {
            "success": False,
            "transaction_id": transaction_id,
            "error": "Unable to determine fraud risk.",
        }

    risk_result = calculate_risk(detection_result)

    related_transactions = get_account_transactions(
        transaction["account_id"]
    )

    response = determine_response(
        risk_result=risk_result,
        transaction=transaction,
        related_transactions=related_transactions,
    )

    return {
        "success": True,
        "transaction_id": transaction_id,
        "account_id": transaction["account_id"],
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "signals": risk_result["signals"],
        "actions": response["actions"],
    }