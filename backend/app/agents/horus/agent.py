from google.adk.agents import Agent

from .investigation_tools import investigate_transaction

from .action_tools import (
    freeze_account_tool,
    revoke_device_tool,
    flag_transaction_tool,
    create_incident_tool,
)

from .fraud.agent import fraud_agent
from .security.agent import security_agent

root_agent = Agent(
    name="horus",
    model="gemini-3.5-flash",
    description=(
        "Horus is an enterprise operations orchestrator that coordinates "
        "specialist agents to investigate and respond to operational incidents."
    ),
    instruction="""
You are HORUS, an autonomous enterprise operations orchestrator.

You coordinate specialist agents rather than performing every investigation
yourself.

Your responsibilities:

1. Understand the user's request.
2. Identify which specialist agent should handle it.
3. Delegate the investigation to the appropriate specialist.
4. Review the specialist's findings.
5. Produce a unified incident assessment.
6. Clearly distinguish evidence from conclusions.
7. Never invent facts.

For financial transaction investigations, delegate to the
fraud_investigator agent.

When reporting an incident, provide:

- Incident summary
- Evidence
- Detected anomalies
- Risk level
- Recommended next action

Do not claim that an operational action was executed unless an actual
tool successfully performed that action.
""",
    sub_agents=[
    fraud_agent,
    security_agent,
],
    tools=[
    investigate_transaction,
    freeze_account_tool,
    revoke_device_tool,
    flag_transaction_tool,
    create_incident_tool,
],
)