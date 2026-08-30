from detection.transaction_detector import detect_transaction
from detection.risk_engine import calculate_risk
from agents.horus.investigation_tools import investigate_transaction
from agents.horus.response_tools import determine_transaction_response

def test_transaction_exists():
    result = detect_transaction("TX-FRAUD-001")

    assert result["found"] is True
    assert result["transaction_id"] == "TX-FRAUD-001"
    assert result["account_id"] == "ACC-2048"


def test_fraud_risk_is_critical():
    detection = detect_transaction("TX-FRAUD-001")
    risk = calculate_risk(detection)

    assert risk["risk_score"] == 100
    assert risk["risk_level"] == "CRITICAL"


def test_all_expected_fraud_signals_trigger():
    detection = detect_transaction("TX-FRAUD-001")
    risk = calculate_risk(detection)

    triggered_rules = {
        rule["rule"]
        for rule in risk["rule_results"]
        if rule["triggered"]
    }

    assert triggered_rules == {
        "AMOUNT_ANOMALY",
        "NEW_DEVICE",
        "GEOGRAPHIC_ANOMALY",
        "TRANSACTION_VELOCITY",
    }


def test_investigation_returns_enterprise_evidence():
    result = investigate_transaction("TX-FRAUD-001")

    assert result["found"] is True

    assert result["transaction"]["transaction_id"] == "TX-FRAUD-001"
    assert result["transaction"]["account_id"] == "ACC-2048"

    assert result["account"]["account_id"] == "ACC-2048"

    assert result["historical_baseline"]["transaction_count"] == 51

    assert "DEV-99999" in result["historical_baseline"]["untrusted_devices"]

    assert result["security_context"]["untrusted_device_count"] == 2


def test_response_policy_produces_critical_containment_plan():
    result = determine_transaction_response("TX-FRAUD-001")

    assert result["success"] is True
    assert result["risk_score"] == 100
    assert result["risk_level"] == "CRITICAL"

    actions = result["actions"]
    action_types = [action["action"] for action in actions]

    assert action_types == [
        "FREEZE_ACCOUNT",
        "REVOKE_DEVICE",
        "FLAG_TRANSACTIONS",
        "CREATE_INCIDENT",
    ]


def test_response_policy_flags_related_transactions():
    result = determine_transaction_response("TX-FRAUD-001")

    flag_action = next(
        action
        for action in result["actions"]
        if action["action"] == "FLAG_TRANSACTIONS"
    )

    assert set(flag_action["transaction_ids"]) == {
        "TX-FRAUD-001",
        "TX-FRAUD-002",
        "TX-FRAUD-003",
    }


def test_missing_transaction_is_handled():
    detection = detect_transaction("TX-DOES-NOT-EXIST")

    assert detection["found"] is False


def test_missing_transaction_response_fails_cleanly():
    result = determine_transaction_response("TX-DOES-NOT-EXIST")

    assert result["success"] is False
    assert result["transaction_id"] == "TX-DOES-NOT-EXIST"