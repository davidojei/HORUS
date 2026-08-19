"""
HORUS Risk Engine.

Converts detection signals into a normalized risk score
and risk classification.
"""


def calculate_risk(detection_result: dict) -> dict:
    """
    Calculate the final transaction risk level.
    """

    if not detection_result.get("found"):
        return {
            "risk_score": 0,
            "risk_level": "UNKNOWN",
            "signals": [],
        }

    raw_score = detection_result.get(
        "raw_score",
        0,
    )

    # Normalize to a maximum of 100.
    risk_score = min(raw_score, 100)

    if risk_score >= 70:
        risk_level = "CRITICAL"

    elif risk_score >= 45:
        risk_level = "HIGH"

    elif risk_score >= 20:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    signals = [
        rule["rule"]
        for rule in detection_result.get(
            "triggered_rules",
            [],
        )
    ]

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "signals": signals,
        "rule_results": detection_result.get(
            "triggered_rules",
            [],
        ),
    }