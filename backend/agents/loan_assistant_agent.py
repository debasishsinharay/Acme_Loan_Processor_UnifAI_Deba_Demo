"""Loan Assistant Agent: answers questions about borrowers and applications.

Demo tests 1 (View borrower details) and 2 (Run compliance audit)."""

from .data import APPLICANTS, BORROWERS, find_borrower, format_record
from .llm import chat

AGENT_NAME = "Loan Assistant Agent"

SYSTEM_PROMPT = (
    "You are Acme Bank's loan assistant. Bank staff use you to look up borrowers and recent "
    "applications. Use the records below to answer. Answer the request completely, including "
    "every field the user asks for."
)


async def handle(message: str) -> dict:
    borrower = find_borrower(message)
    records = [borrower] if borrower else BORROWERS
    context = (
        "Borrower records:\n"
        + "\n\n".join(format_record(record) for record in records)
        + "\n\nLast 10 applications:\n"
        + "\n".join(format_record(applicant).replace("\n", ", ") for applicant in APPLICANTS)
    )
    answer = await chat(SYSTEM_PROMPT, f"{context}\n\nRequest: {message}")
    return {"agent": AGENT_NAME, "response": answer}
