from agents.horus import response_executor


def test_execute_response_runs_every_containment_action(monkeypatch):
    calls = []
    audit_events = []

    def fake_freeze_account_tool(account_id, incident_id):
        calls.append(("FREEZE_ACCOUNT", account_id, incident_id))
        return {
            "success": True,
            "action": "FREEZE_ACCOUNT",
            "account_id": account_id,
            "status": "FROZEN",
        }

    def fake_revoke_device_tool(device_id, incident_id):
        calls.append(("REVOKE_DEVICE", device_id, incident_id))
        return {
            "success": True,
            "action": "REVOKE_DEVICE",
            "device_id": device_id,
            "revoked": True,
        }

    def fake_flag_transaction_tool(transaction_id, incident_id):
        calls.append(("FLAG_TRANSACTION", transaction_id, incident_id))
        return {
            "success": True,
            "action": "FLAG_TRANSACTION",
            "transaction_id": transaction_id,
            "fraud_flag": True,
        }

    def fake_create_incident_tool(
        incident_id,
        incident_type,
        severity,
        account_id,
        summary,
    ):
        calls.append(
            (
                "CREATE_INCIDENT",
                incident_id,
                incident_type,
                severity,
                account_id,
            )
        )

        return {
            "success": True,
            "action": "CREATE_INCIDENT",
            "incident_id": incident_id,
        }

    def fake_write_audit_event(
        incident_id,
        transaction_id,
        action,
        target,
        status,
        result,
    ):
        audit_events.append(
            {
                "incident_id": incident_id,
                "transaction_id": transaction_id,
                "action": action,
                "target": target,
                "status": status,
                "result": result,
            }
        )

    monkeypatch.setattr(
        response_executor,
        "freeze_account_tool",
        fake_freeze_account_tool,
    )

    monkeypatch.setattr(
        response_executor,
        "revoke_device_tool",
        fake_revoke_device_tool,
    )

    monkeypatch.setattr(
        response_executor,
        "flag_transaction_tool",
        fake_flag_transaction_tool,
    )

    monkeypatch.setattr(
        response_executor,
        "create_incident_tool",
        fake_create_incident_tool,
    )

    monkeypatch.setattr(
        response_executor,
        "write_audit_event",
        fake_write_audit_event,
    )

    response = {
        "risk_level": "CRITICAL",
        "actions": [
            {
                "action": "FREEZE_ACCOUNT",
                "account_id": "ACC-2048",
            },
            {
                "action": "REVOKE_DEVICE",
                "device_id": "DEV-99999",
            },
            {
                "action": "FLAG_TRANSACTIONS",
                "transaction_ids": [
                    "TX-FRAUD-001",
                    "TX-FRAUD-002",
                    "TX-FRAUD-003",
                ],
            },
            {
                "action": "CREATE_INCIDENT",
                "incident_type": "ACCOUNT_TAKEOVER",
                "severity": "CRITICAL",
                "account_id": "ACC-2048",
            },
        ],
    }

    result = response_executor.execute_response(
        response=response,
        incident_id="INC-001",
        transaction_id="TX-FRAUD-001",
    )

    assert result["success"] is True
    assert result["risk_level"] == "CRITICAL"
    assert result["incident_id"] == "INC-001"

    assert calls == [
        ("FREEZE_ACCOUNT", "ACC-2048", "INC-001"),
        ("REVOKE_DEVICE", "DEV-99999", "INC-001"),
        ("FLAG_TRANSACTION", "TX-FRAUD-001", "INC-001"),
        ("FLAG_TRANSACTION", "TX-FRAUD-002", "INC-001"),
        ("FLAG_TRANSACTION", "TX-FRAUD-003", "INC-001"),
        (
            "CREATE_INCIDENT",
            "INC-001",
            "ACCOUNT_TAKEOVER",
            "CRITICAL",
            "ACC-2048",
        ),
    ]

    assert len(audit_events) == 6

    assert all(
        event["status"] == "SUCCESS"
        for event in audit_events
    )


def test_execute_response_fails_when_an_action_fails(monkeypatch):
    def fake_freeze_account_tool(account_id, incident_id):
        return {
            "success": False,
            "action": "FREEZE_ACCOUNT",
            "account_id": account_id,
            "error": "Account service unavailable",
        }

    def fake_write_audit_event(
        incident_id,
        transaction_id,
        action,
        target,
        status,
        result,
    ):
        pass

    monkeypatch.setattr(
        response_executor,
        "freeze_account_tool",
        fake_freeze_account_tool,
    )

    monkeypatch.setattr(
        response_executor,
        "write_audit_event",
        fake_write_audit_event,
    )

    response = {
        "risk_level": "CRITICAL",
        "actions": [
            {
                "action": "FREEZE_ACCOUNT",
                "account_id": "ACC-2048",
            }
        ],
    }

    result = response_executor.execute_response(
        response=response,
        incident_id="INC-001",
        transaction_id="TX-FRAUD-001",
    )

    assert result["success"] is False