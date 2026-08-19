"""
HORUS Fraud Detection Rules.

Individual rules used by the transaction detection engine.
Each rule returns a consistent detection result containing:

- rule
- triggered
- score
- reason
"""


def check_amount_anomaly(
    transaction: dict,
    account_transactions: list,
) -> dict:
    """
    Detect transactions that are unusually large compared
    with the account's historical transaction behavior.
    """

    amount = transaction["amount"]

    historical = [
        tx["amount"]
        for tx in account_transactions
        if tx["transaction_id"] != transaction["transaction_id"]
    ]

    if not historical:
        return {
            "rule": "AMOUNT_ANOMALY",
            "triggered": False,
            "score": 0,
            "reason": "No historical transactions available.",
        }

    historical_max = max(historical)
    historical_average = sum(historical) / len(historical)

    # Extremely large compared with historical behavior.
    if amount >= historical_max * 5:
        return {
            "rule": "AMOUNT_ANOMALY",
            "triggered": True,
            "score": 30,
            "reason": (
                f"Transaction amount {amount:,.0f} NGN is more than "
                f"5x the historical maximum of {historical_max:,.0f} NGN."
            ),
        }

    if amount >= historical_average * 3:
        return {
            "rule": "AMOUNT_ANOMALY",
            "triggered": True,
            "score": 20,
            "reason": (
                f"Transaction amount {amount:,.0f} NGN is more than "
                f"3x the historical average of "
                f"{historical_average:,.0f} NGN."
            ),
        }

    return {
        "rule": "AMOUNT_ANOMALY",
        "triggered": False,
        "score": 0,
        "reason": "Transaction amount is within expected historical range.",
    }


def check_new_device(
    transaction: dict,
    devices: list,
) -> dict:
    """
    Detect transactions originating from a new or untrusted device.

    Detection is based on the device's trust/registration state,
    not on response actions that HORUS may have taken later.
    """

    device_id = transaction["device_id"]

    matching_devices = [
        device
        for device in devices
        if device["device_id"] == device_id
    ]

    # Device does not exist in the account's known devices.
    if not matching_devices:
        return {
            "rule": "NEW_DEVICE",
            "triggered": True,
            "score": 30,
            "reason": (
                f"Device {device_id} is not registered on the account."
            ),
        }

    device = matching_devices[0]

    # The important detection signal is that the device is untrusted.
    if not device.get("trusted", False):
        return {
            "rule": "NEW_DEVICE",
            "triggered": True,
            "score": 30,
            "reason": (
                f"Device {device_id} is untrusted and was used "
                f"for the transaction."
            ),
        }

    return {
        "rule": "NEW_DEVICE",
        "triggered": False,
        "score": 0,
        "reason": (
            f"Device {device_id} is a trusted device."
        ),
    }

def check_geographic_anomaly(
    transaction: dict,
    account: dict,
    devices: list,
) -> dict:
    """
    Detect transactions occurring outside the account's
    historical/home location.
    """

    transaction_location = transaction["location"]
    account_location = account.get("city")

    if not account_location:
        return {
            "rule": "GEOGRAPHIC_ANOMALY",
            "triggered": False,
            "score": 0,
            "reason": "Account location unavailable.",
        }

    if transaction_location.lower() != account_location.lower():
        return {
            "rule": "GEOGRAPHIC_ANOMALY",
            "triggered": True,
            "score": 20,
            "reason": (
                f"Transaction occurred in {transaction_location}, "
                f"while the account is registered in {account_location}."
            ),
        }

    return {
        "rule": "GEOGRAPHIC_ANOMALY",
        "triggered": False,
        "score": 0,
        "reason": (
            f"Transaction location {transaction_location} "
            f"matches account location."
        ),
    }


def check_transaction_velocity(
    transaction: dict,
    account_transactions: list,
) -> dict:
    """
    Detect multiple transactions occurring at the same timestamp.
    """

    timestamp = transaction["timestamp"]

    concurrent_transactions = [
        tx
        for tx in account_transactions
        if tx["timestamp"] == timestamp
    ]

    count = len(concurrent_transactions)

    if count >= 3:
        total_amount = sum(
            tx["amount"]
            for tx in concurrent_transactions
        )

        return {
            "rule": "TRANSACTION_VELOCITY",
            "triggered": True,
            "score": 30,
            "reason": (
                f"{count} transactions occurred at the exact same "
                f"timestamp with a combined value of "
                f"{total_amount:,.0f} NGN."
            ),
        }

    if count == 2:
        return {
            "rule": "TRANSACTION_VELOCITY",
            "triggered": True,
            "score": 15,
            "reason": (
                f"{count} transactions occurred at the exact "
                f"same timestamp."
            ),
        }

    return {
        "rule": "TRANSACTION_VELOCITY",
        "triggered": False,
        "score": 0,
        "reason": "No abnormal transaction velocity detected.",
    }