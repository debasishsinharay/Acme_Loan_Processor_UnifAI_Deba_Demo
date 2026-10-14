"""Runs one Python expression from the DTI agent: ``python formula_sandbox.py EXPR ALLOWED_JSON``.

It runs in its own process with a 5 second limit (set by the caller). An audit hook lets a
shell command run only if it is on the allowed list (hostname, whoami, ...) and blocks
other processes, network access and file writes, so the demo can show a command running
on the server without opening the server to arbitrary commands. Keep this file out of the
UnifAI scan scope: it is demo infrastructure, not part of the app being secured.
"""
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
