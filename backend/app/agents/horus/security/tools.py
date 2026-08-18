from services.data_service import (
    get_account,
    get_account_devices,
    get_account_logins,
)


def investigate_account_security(account_id: str) -> dict:
    """
    Investigate authentication, device, and geographic security signals
    for an enterprise account.
    """

    account = get_account(account_id)
    devices = get_account_devices(account_id)
    logins = get_account_logins(account_id)

    return {
        "account": account,
        "devices": devices,
        "logins": logins,
    }