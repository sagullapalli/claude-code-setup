"""CLI runner for the News Research Agent.

Provides an interactive command-line interface to chat with the news agent.
Type your topic and press Enter. Type 'quit' or 'exit' to stop.

Usage:
    python run_cli.py
"""

import asyncio

from google.adk.runners import InMemoryRunner
from google.genai import types

from news_agent.agent import root_agent


async def main() -> None:
    """Run the news agent in an interactive CLI loop."""
    runner = InMemoryRunner(agent=root_agent, app_name="news_app")

    # Create a session
    user_id = "cli_user"
    session_id = "cli_session"
    await runner.session_service.create_session(
        app_name="news_app",
        user_id=user_id,
        session_id=session_id,
    )

    print("=" * 60)
    print("  News Research Agent")
    print("  Ask about any topic to get recent news.")
    print("  Type 'quit' or 'exit' to stop.")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        message = types.Content(
            role="user",
            parts=[types.Part(text=user_input)],
        )

        print("\nAgent: ", end="", flush=True)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text.strip())
        print()


if __name__ == "__main__":
    asyncio.run(main())
