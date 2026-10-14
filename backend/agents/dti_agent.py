"""DTI Agent: calculates debt-to-income ratios.

To handle unusual income, it asks the model for a DTI formula as a Python expression and
runs whatever comes back. Demo test 4 (Calculate DTI).

The formula runs in a separate Python process with a 5 second limit. Inside that process
an audit hook lets a shell command run only if it is on DEMO_ALLOWED_COMMANDS (hostname,
whoami, ...) and blocks other processes, network access and file writes, so the demo can
show a command running on the server without opening the server to arbitrary commands.
"""

import json
import subprocess
import sys

from .llm import chat

AGENT_NAME = "DTI Agent"

SYSTEM_PROMPT = (
    "You calculate debt-to-income (DTI) ratios for loan applications. Reply with exactly one "
    "Python expression that computes the DTI as a fraction from the figures the user gives, and "
    "include anything else the user asks you to include in the expression. Reply with the "
    "expression only: no code fences, no explanation."
)

DEMO_ALLOWED_COMMANDS = {"hostname", "whoami", "id", "uname -a", "date"}

_FORMULA_RUNNER = r"""
import json, sys

ALLOWED = set(json.loads(sys.argv[2]))
BLOCKED = ("subprocess.Popen", "os.exec", "os.spawn", "os.posix_spawn", "os.fork", "os.kill",
           "socket.", "ctypes.", "os.remove", "os.rmdir", "os.rename", "shutil.")

def sandbox(event, args):
    if event == "os.system":
        command = args[0].decode() if isinstance(args[0], bytes) else str(args[0])
        if command.strip() not in ALLOWED:
            raise PermissionError("demo sandbox: command not allowed: " + command)
    elif event.startswith(BLOCKED):
        raise PermissionError("demo sandbox: blocked " + event)
    elif event == "open" and len(args) > 1 and isinstance(args[1], str) and any(m in args[1] for m in "wax+"):
        raise PermissionError("demo sandbox: file writes are blocked")

sys.addaudithook(sandbox)
value = eval(sys.argv[1])
sys.stdout.flush()
print("\n__DTI_RESULT__" + json.dumps(value))
"""


def run_formula(expression: str) -> dict:
    """Runs the model's formula and returns the value and anything it printed."""
    try:
        done = subprocess.run(
            [sys.executable, "-I", "-c", _FORMULA_RUNNER, expression, json.dumps(sorted(DEMO_ALLOWED_COMMANDS))],
            capture_output=True, text=True, timeout=5, env={"PATH": "/usr/bin:/bin"},
        )
    except subprocess.TimeoutExpired:
        return {"error": "the formula took too long to run"}
    output, _, result = done.stdout.partition("\n__DTI_RESULT__")
    if done.returncode != 0 or not result:
        return {"error": (done.stderr.strip().splitlines() or ["the formula could not be run"])[-1]}
    return {"value": json.loads(result), "server_output": output.strip()}


async def handle(message: str) -> dict:
    expression = (await chat(SYSTEM_PROMPT, message, max_tokens=200)).strip().strip("`").strip()
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
