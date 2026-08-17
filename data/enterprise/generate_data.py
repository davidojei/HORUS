import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

BASE_DIR = Path(__file__).parent


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

NUM_ACCOUNTS = 1000
NUM_TRANSACTIONS = 50000
NUM_DEVICES = 2000
NUM_LOGIN_EVENTS = 20000

CITIES = [
    "Lagos",
    "Abuja",
    "Port Harcourt",
    "Ibadan",
    "Kano",
    "Benin City",
    "Enugu",
]

MERCHANTS = [
    "Shoprite",
    "Jumia",
    "Amazon",
    "Global Electronics",
    "QuickMart",
    "Tech World",
    "Supermart",
    "Fashion Hub",
]

ACCOUNT_TYPES = [
    "PERSONAL",
    "BUSINESS",
]

BASE_DATE = datetime(2026, 8, 1)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def random_date(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def write_json(filename, data):
    path = BASE_DIR / filename

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    print(f"Generated {len(data):,} records -> {path}")


# ---------------------------------------------------------
# Accounts
# ---------------------------------------------------------

def generate_accounts():
    accounts = []

    for i in range(NUM_ACCOUNTS):
        account_id = f"ACC-{2000 + i}"

        accounts.append({
            "account_id": account_id,
            "customer_name": f"Customer {i + 1}",
            "country": "Nigeria",
            "city": random.choice(CITIES),
            "account_type": random.choice(ACCOUNT_TYPES),
            "risk_score": random.randint(5, 40),
            "status": "ACTIVE",
            "created_at": random_date(
                datetime(2020, 1, 1),
                BASE_DATE,
            ).isoformat(),
        })

    return accounts


# ---------------------------------------------------------
# Devices
# ---------------------------------------------------------

def generate_devices(accounts):
    devices = []

    for i in range(NUM_DEVICES):
        device_id = f"DEV-{9000 + i}"

        account = random.choice(accounts)

        devices.append({
            "device_id": device_id,
            "account_id": account["account_id"],
            "first_seen": random_date(
                datetime(2024, 1, 1),
                BASE_DATE,
            ).isoformat(),
            "location": account["city"],
            "trusted": random.random() > 0.15,
        })

    return devices


# ---------------------------------------------------------
# Transactions
# ---------------------------------------------------------

def generate_transactions(accounts, devices):
    transactions = []

    account_devices = {}

    for device in devices:
        account_devices.setdefault(
            device["account_id"],
            []
        ).append(device)

    for i in range(NUM_TRANSACTIONS):
        account = random.choice(accounts)

        account_id = account["account_id"]

        available_devices = account_devices.get(account_id, [])

        if available_devices:
            device = random.choice(available_devices)
            device_id = device["device_id"]
        else:
            device_id = f"DEV-{random.randint(9000, 10999)}"

        amount = random.randint(2_000, 75_000)

        transactions.append({
            "transaction_id": f"TX-{10000 + i}",
            "account_id": account_id,
            "amount": amount,
            "currency": "NGN",
            "merchant": random.choice(MERCHANTS),
            "location": account["city"],
            "device_id": device_id,
            "timestamp": random_date(
                BASE_DATE,
                datetime(2026, 8, 17),
            ).isoformat(),
            "status": "COMPLETED",
        })

    return transactions


# ---------------------------------------------------------
# Login Events
# ---------------------------------------------------------

def generate_login_events(accounts, devices):
    events = []

    account_devices = {}

    for device in devices:
        account_devices.setdefault(
            device["account_id"],
            []
        ).append(device)

    for i in range(NUM_LOGIN_EVENTS):
        account = random.choice(accounts)

        account_id = account["account_id"]

        available_devices = account_devices.get(account_id, [])

        if available_devices:
            device = random.choice(available_devices)
        else:
            device = random.choice(devices)

        events.append({
            "event_id": f"LOGIN-{8000 + i}",
            "account_id": account_id,
            "device_id": device["device_id"],
            "ip_address": (
                f"197.{random.randint(1, 254)}."
                f"{random.randint(1, 254)}."
                f"{random.randint(1, 254)}"
            ),
            "location": device["location"],
            "timestamp": random_date(
                BASE_DATE,
                datetime(2026, 8, 17),
            ).isoformat(),
            "success": True,
        })

    return events


# ---------------------------------------------------------
# Inject Fraud Scenario
# ---------------------------------------------------------

def inject_account_takeover(
    accounts,
    transactions,
    devices,
    login_events,
):
    """
    Creates a deliberately suspicious account takeover scenario.
    """

    account_id = "ACC-2048"

    suspicious_device = {
        "device_id": "DEV-99999",
        "account_id": account_id,
        "first_seen": "2026-08-17T14:29:00",
        "location": "Lagos",
        "trusted": False,
    }

    devices.append(suspicious_device)

    login_events.append({
        "event_id": "LOGIN-99999",
        "account_id": account_id,
        "device_id": "DEV-99999",
        "ip_address": "197.210.45.21",
        "location": "Lagos",
        "timestamp": "2026-08-17T14:29:51",
        "success": True,
    })

    suspicious_transactions = [
    ("TX-FRAUD-001", 485000),
    ("TX-FRAUD-002", 720000),
    ("TX-FRAUD-003", 610000),
    ]

    for transaction_id, amount in suspicious_transactions:
        transactions.append({
            "transaction_id": transaction_id,
            "account_id": account_id,
            "amount": amount,
            "currency": "NGN",
            "merchant": "Global Electronics",
            "location": "Lagos",
            "device_id": "DEV-99999",
            "timestamp": "2026-08-17T14:32:11",
            "status": "COMPLETED",
        })

    print("Injected incident: INC-001 Account Takeover")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("Generating Horus enterprise dataset...\n")

    accounts = generate_accounts()

    devices = generate_devices(accounts)

    transactions = generate_transactions(
        accounts,
        devices,
    )

    login_events = generate_login_events(
        accounts,
        devices,
    )

    inject_account_takeover(
        accounts,
        transactions,
        devices,
        login_events,
    )

    write_json(
        "accounts.json",
        accounts,
    )

    write_json(
        "transactions.json",
        transactions,
    )

    write_json(
        "devices.json",
        devices,
    )

    write_json(
        "login_events.json",
        login_events,
    )

    print("\nHorus enterprise dataset generated successfully.")


if __name__ == "__main__":
    main()