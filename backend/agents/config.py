"""Settings shared by the agents."""

import os


def openrouter_key() -> str:
    """The OpenRouter API key from .env."""
    return os.getenv("OPENROUTER_API_KEY", "").strip()
