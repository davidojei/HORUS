from services.action_service import (
    freeze_account,
    revoke_device,
    flag_transaction,
    create_incident,
)


def freeze_account_tool(account_id: str, incident_id: str):
    """
    Freeze an enterprise account.

    Use when Horus determines that an account is actively compromised
    and immediate containment is required.
    """

    return freeze_account(
        account_id=account_id,
        incident_id=incident_id,
    )


def revoke_device_tool(device_id: str, incident_id: str):
    """
    Revoke an untrusted or compromised device.
    """

    return revoke_device(
        device_id=device_id,
        incident_id=incident_id,
    )


def flag_transaction_tool(
    transaction_id: str,
    incident_id: str,
):
    """
    Flag a transaction for fraud review and potential reversal.
    """

    return flag_transaction(
        transaction_id=transaction_id,
        incident_id=incident_id,
    )


def create_incident_tool(
    incident_id: str,
    incident_type: str,
    severity: str,
    account_id: str,
    summary: str,
):
    """
    Create a persistent enterprise incident record.
    """

    return create_incident(
        incident_id=incident_id,
        incident_type=incident_type,
        severity=severity,
        account_id=account_id,
        summary=summary,
    )