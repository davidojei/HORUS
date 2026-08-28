from services.data_service import (
    get_account,
    get_transaction,
    get_account_transactions,
    get_account_devices,
    get_account_logins,
)

from detection.transaction_detector import detect_transaction


def investigate_transaction(transaction_id: str) -> dict:
    """
    Investigate a transaction and return a compact,
    evidence-focused representation suitable for the HORUS agent.

    Raw account data remains available to the deterministic
    detection layer, but the LLM receives only relevant evidence.
    """

    transaction = get_transaction(transaction_id)

    if not transaction:
        return {
            "found": False,
            "message": f"Transaction {transaction_id} was not found.",
        }

    account_id = transaction["account_id"]

    account = get_account(account_id)

    account_transactions = get_account_transactions(account_id)
    devices = get_account_devices(account_id)
    login_events = get_account_logins(account_id)

    # --------------------------------------------------
    # Run deterministic detection
    # --------------------------------------------------

    detection_result = detect_transaction(transaction_id)

    # --------------------------------------------------
    # Compact transaction history
    # --------------------------------------------------

    historical_amounts = [
        tx["amount"]
        for tx in account_transactions
        if isinstance(tx.get("amount"), (int, float))
    ]

    historical_average = (
        sum(historical_amounts) / len(historical_amounts)
        if historical_amounts
        else 0
    )

    historical_max = (
        max(historical_amounts)
        if historical_amounts
        else 0
    )

    trusted_devices = [
        device["device_id"]
        for device in devices
        if device.get("trusted") is True
    ]

    untrusted_devices = [
        device["device_id"]
        for device in devices
        if device.get("trusted") is False
    ]

    historical_locations = sorted(
        {
            tx.get("location")
            for tx in account_transactions
            if tx.get("location")
        }
    )

    # --------------------------------------------------
    # Return compact evidence
    # --------------------------------------------------

    return {
        "found": True,

        "transaction": transaction,

        "account": {
            "account_id": account.get("account_id"),
            "customer_name": account.get("customer_name"),
            "country": account.get("country"),
            "city": account.get("city"),
            "account_type": account.get("account_type"),
            "risk_score": account.get("risk_score"),
            "status": account.get("status"),
        },

        "historical_baseline": {
            "transaction_count": len(account_transactions),
            "average_amount": round(historical_average, 2),
            "maximum_amount": historical_max,
            "historical_locations": historical_locations,
            "trusted_devices": trusted_devices,
            "untrusted_devices": untrusted_devices,
        },

        "security_context": {
            "known_device_count": len(devices),
            "untrusted_device_count": len(untrusted_devices),
            "login_event_count": len(login_events),
        },

        "detection": detection_result,
    }