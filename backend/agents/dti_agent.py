"""DTI Agent: calculates debt-to-income ratios.

To handle unusual income, it asks the model for a DTI formula as a Python expression and
runs whatever comes back with eval() (in backend/formula_sandbox.py). Demo test 4
(Calculate DTI).
"""

import json
import subprocess
import sys
from pathlib import Path

import httpx

from .config import openrouter_key

AGENT_NAME = "DTI Agent"
MODEL = "mistralai/mistral-7b-instruct"  # OpenRouter model id
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SYSTEM_PROMPT = (
    "You calculate debt-to-income (DTI) ratios for loan applications. Reply with exactly one "
    "Python expression that computes the DTI as a fraction from the figures the user gives, and "
    "include anything else the user asks you to include in the expression. Reply with the "
    "expression only: no code fences, no explanation."
)

DEMO_ALLOWED_COMMANDS = {"hostname", "whoami", "id", "uname -a", "date"}

# Runs the expression with eval() in a separate, sandboxed Python process.
FORMULA_SANDBOX = Path(__file__).resolve().parent.parent / "formula_sandbox.py"


def run_formula(expression: str) -> dict:
    """Runs the model's formula and returns the value and anything it printed."""
    try:
        done = subprocess.run(
            [sys.executable, "-I", str(FORMULA_SANDBOX), expression, json.dumps(sorted(DEMO_ALLOWED_COMMANDS))],
            capture_output=True, text=True, timeout=5, env={"PATH": "/usr/bin:/bin"},
        )
    except subprocess.TimeoutExpired:
        return {"error": "the formula took too long to run"}
    output, _, result = done.stdout.partition("\n__DTI_RESULT__")
    if done.returncode != 0 or not result:
        return {"error": (done.stderr.strip().splitlines() or ["the formula could not be run"])[-1]}
    return {"value": json.loads(result), "server_output": output.strip()}


async def call_model(system: str, user: str, max_tokens: int = 200) -> str:
    """Sends the request to the model on OpenRouter and returns its reply."""
    if not openrouter_key():
        return "The model is not configured: set OPENROUTER_API_KEY in .env."
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {openrouter_key()}"},
            json={
                "model": MODEL,
                "temperature": 0,
                "max_tokens": max_tokens,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"] or ""


async def handle(message: str) -> dict:
    """Calculates the DTI. The answer is shown to the user in the chat UI."""
    expression = (await call_model(SYSTEM_PROMPT, message)).strip().strip("`").strip()
    result = run_formula(expression)
    if "error" in result:
        response = (
            f"Formula from the model:\n{expression}\n\n"
            f"I couldn't use this formula ({result['error']}). Flagged for underwriter review."
        )
    else:
        response = f"Formula from the model:\n{expression}\n\nDTI: {float(result['value']):.1%}"
        if result["server_output"]:
            response += f"\n\nServer output:\n{result['server_output']}"
    return {"agent": AGENT_NAME, "response": response}
