import asyncio
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.horus.agent import root_agent

async def main():
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="horus",
        session_service=session_service,
    )

    user_id = "demo_user"
    session_id = "demo_session"

    await session_service.create_session(
        app_name="horus",
        user_id=user_id,
        session_id=session_id,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="Investigate TX-FRAUD-001 and exepcute the recommended containment actions."
            )
        ],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)


if __name__ == "__main__":
    asyncio.run(main())