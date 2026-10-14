"""OpenRouter chat client shared by the agents."""

import os

import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def chat(system: str, user: str, max_tokens: int = 600) -> str:
    """Send one system + user message to the model and return its reply."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-4-scout").strip()
    if not api_key:
        return "The model is not configured: set OPENROUTER_API_KEY in .env."
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
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
