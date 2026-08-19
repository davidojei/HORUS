"""
HORUS Transaction Detection Engine.

Combines individual fraud rules into a structured
transaction-level detection result.
"""

from .rules import (
    check_amount_anomaly,
    check_new_device,
    check_geographic_anomaly,
    check_transaction_velocity,
)

from services.data_service import (
    get_transaction,
    get_account,
    get_account_transactions,
    get_account_devices,
)


def detect_transaction(transaction_id: str) -> dict:
    """
    Run all fraud detection rules against a transaction.
    """

    transaction = get_transaction(transaction_id)

    if not transaction:
        return {
            "found": False,
            "transaction_id": transaction_id,
            "message": f"Transaction {transaction_id} was not found.",
        }

    account_id = transaction["account_id"]

    account = get_account(account_id)

    account_transactions = get_account_transactions(
        account_id
    )

    devices = get_account_devices(
        account_id
    )

    rules = [
        check_amount_anomaly(
            transaction,
            account_transactions,
        ),
        check_new_device(
            transaction,
            devices,
        ),
        check_geographic_anomaly(
            transaction,
            account,
            devices,
        ),
        check_transaction_velocity(
            transaction,
            account_transactions,
        ),
    ]

    triggered_rules = [
        rule
        for rule in rules
        if rule["triggered"]
    ]

    total_score = sum(
        rule["score"]
        for rule in triggered_rules
    )

    return {
        "found": True,
        "transaction_id": transaction_id,
        "account_id": account_id,
        "rules": rules,
        "triggered_rules": triggered_rules,
        "raw_score": total_score,
    }