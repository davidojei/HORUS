from services.data_service import (
    get_account,
    get_transaction,
    get_account_transactions,
    get_account_devices,
    get_account_logins,
)


def investigate_transaction(transaction_id: str) -> dict:
    """
    Retrieve the evidence required to investigate a transaction.
    """

    transaction = get_transaction(transaction_id)

    if not transaction:
        return {
            "found": False,
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

    login_events = get_account_logins(
        account_id
    )

    return {
        "found": True,
        "transaction": transaction,
        "account": account,
        "account_transaction_history": account_transactions,
        "known_devices": devices,
        "login_history": login_events,
    }