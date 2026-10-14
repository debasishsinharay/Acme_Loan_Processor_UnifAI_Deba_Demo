# Acme Loan Processor: UnifAI demo

An AI loan assistant built to show four UnifAI policies, each with one button. A **Secured by
UnifAI** switch in the header runs every test with UnifAI's fixes on or off, in the same build.

| Button | Agent | Policy | UnifAI off | UnifAI on |
|---|---|---|---|---|
| View borrower details | Loan Assistant | Mask PII on user interfaces | SSN, DOB and address shown in full | SSN cut to last 4, DOB and address masked |
| Run compliance audit | Loan Assistant | Malicious content via encoded prompts | Base64 instruction decoded and followed | Instruction removed before the model sees it |
| Analyze financial report | Document | Prompt injection in user inputs and file contents | Hidden "approve this applicant" instruction followed | Hidden blocks removed; real numbers analyzed |
| Calculate DTI | DTI | Validate LLM output for eval / dynamic code execution | Model's formula runs a command on the server | Formula rejected, nothing runs |

## Layout

```
backend/
  main.py                    FastAPI app: POST /chat
  unifai_toggle.py           the on/off switch for UnifAI's fixes (keep out of the scan)
  agents/                    scan this folder with UnifAI
    orchestrator.py          routes a request to one agent
    loan_assistant_agent.py  tests 1 and 2
    document_agent.py        test 3 (the uploaded file goes to the model as raw HTML)
    dti_agent.py             test 4 (runs the model's formula in a sandboxed process)
    llm.py                   OpenRouter client
    data.py                  synthetic borrowers and applications
frontend/                    Next.js chat UI with the switch and the four buttons
  public/demo/               finance_report_hidden.html (test 3) and a clean control copy
.github/                     the Lineaje AI scan workflow
```

## Run it

```bash
cp .env.example .env          # add OPENROUTER_API_KEY
./scripts/run_dev.sh          # backend on :5500, UI on http://localhost:5001
```

or with Docker:

```bash
docker build -t acme-loan-processor .
docker run -d -p 80:5001 -e OPENROUTER_API_KEY=... -e OPENROUTER_MODEL=meta-llama/llama-4-scout acme-loan-processor
```

## Demo flow

1. Run the UnifAI scan on `backend/agents` only (Actions → Lineaje AI Scan → `scan_mode: folder`,
   `folder_path: backend/agents`, `create_fix_pr: true`) and merge the PR. It adds
   `unifai_guard.py` and the guard calls to the agents.
2. Open the app. With the switch **OFF**, click the four buttons: each attack works.
3. Switch it **ON** and click them again: each one is stopped by its policy.

Each answer is labelled with the agent that handled it and whether UnifAI was on.

## How the switch works

UnifAI's fixes call functions in `unifai_guard.py`. `backend/unifai_toggle.py` wraps those
functions when the guard is imported. When the switch is off, the `find_*` checks report
nothing and the other guard functions return their input unchanged, which is how the app
behaved before the fix. Nothing UnifAI wrote is edited, and a rescan keeps working. The
frontend sends the switch state as the `X-UnifAI: on|off` header.

## Safety note for test 4

The DTI agent really runs the model's formula, in a separate Python process with a 5 second
limit. Inside it, only `hostname`, `whoami`, `id`, `uname -a` and `date` may run; other
commands, processes, network access and file writes are blocked. Still, run the demo on an
isolated host.

All borrower and account data is synthetic.
