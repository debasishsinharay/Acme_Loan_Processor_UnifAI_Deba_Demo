"""Orchestrator: sends each chat request to the agent that handles it."""

from . import document_agent, dti_agent, loan_assistant_agent


async def handle_chat(message: str, attachments: list[dict]) -> dict:
    text = message.lower()
    if attachments:
        return await document_agent.handle(message, attachments)
    if "debt-to-income" in text or "dti" in text.split():
        return await dti_agent.handle(message)
    return await loan_assistant_agent.handle(message)
