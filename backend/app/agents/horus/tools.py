TRANSACTIONS = {
    "TX-10492": {
        "transaction_id": "TX-10492",
        "account_id": "ACC-2048",
        "amount": 485000,
        "currency": "NGN",
        "merchant": "Global Electronics",
        "location": "Lagos, Nigeria",
        "device_id": "DEV-9912",
        "timestamp": "2026-08-17T14:32:11",
        "status": "COMPLETED",
    },
    "TX-10501": {
        "transaction_id": "TX-10501",
        "account_id": "ACC-7731",
        "amount": 12000,
        "currency": "NGN",
        "merchant": "QuickMart",
        "location": "Abuja, Nigeria",
        "device_id": "DEV-1821",
        "timestamp": "2026-08-17T14:35:42",
        "status": "COMPLETED",
    },
}


def get_transaction(transaction_id: str) -> dict:
    """
    Retrieve an enterprise transaction by its ID.
    """

    transaction = TRANSACTIONS.get(transaction_id)

    if not transaction:
        return {
            "found": False,
            "transaction_id": transaction_id,
            "message": "Transaction not found.",
        }

    return {
        "found": True,
        "transaction": transaction,
    }