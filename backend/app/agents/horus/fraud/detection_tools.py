from detection.transaction_detector import detect_transaction
from detection.risk_engine import calculate_risk


def detect_transaction_risk(transaction_id: str) -> dict:
    """
    Run HORUS fraud detection rules and calculate
    the final transaction risk.
    """

    detection_result = detect_transaction(transaction_id)

    if not detection_result.get("found"):
        return detection_result

    risk_result = calculate_risk(detection_result)

    return {
        "transaction_id": transaction_id,
        "account_id": detection_result["account_id"],
        "risk_score": risk_result["risk_score"],
        "risk_level": risk_result["risk_level"],
        "signals": risk_result["signals"],
        "rule_results": risk_result["rule_results"],
    }