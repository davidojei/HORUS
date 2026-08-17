import json
from pathlib import Path


DATA_DIR = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "enterprise"
)


def load_json(filename: str):
    path = DATA_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_accounts():
    return load_json("accounts.json")


def get_transactions():
    return load_json("transactions.json")


def get_devices():
    return load_json("devices.json")


def get_login_events():
    return load_json("login_events.json")


def get_account(account_id: str):
    accounts = get_accounts()

    for account in accounts:
        if account["account_id"] == account_id:
            return account

    return None


def get_transaction(transaction_id: str):
    transactions = get_transactions()

    for transaction in transactions:
        if transaction["transaction_id"] == transaction_id:
            return transaction

    return None


def get_account_transactions(account_id: str):
    transactions = get_transactions()

    return [
        transaction
        for transaction in transactions
        if transaction["account_id"] == account_id
    ]


def get_account_devices(account_id: str):
    devices = get_devices()

    return [
        device
        for device in devices
        if device["account_id"] == account_id
    ]


def get_account_logins(account_id: str):
    login_events = get_login_events()

    return [
        event
        for event in login_events
        if event["account_id"] == account_id
    ]