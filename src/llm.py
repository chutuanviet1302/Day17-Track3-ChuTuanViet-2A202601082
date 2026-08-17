"""Thin LLM wrapper for the demo UI chat reply.

This is the ONLY place the lab calls a generative LLM. Benchmark scoring never
uses an LLM (see LAB.md): retrieval evidence is graded deterministically. Here
an LLM only turns retrieved memory context into a grounded assistant reply so
the mini-product feels real.

Providers (first configured wins):
1. Gemini   — GEMINI_API_KEY / GOOGLE_API_KEY, model GEMINI_MODEL (default gemini-2.5-flash-lite)
2. OpenRouter — OPENROUTER_API_KEY, model OPENROUTER_MODEL (default openrouter/auto)
"""

from __future__ import annotations

import os
from typing import Any

import requests

from .config import settings

SYSTEM_INSTRUCTION = (
    "You are the assistant of a personal memory agent for VinUni Lab 17. "
    "Answer the user grounded ONLY in the retrieved memory context provided. "
    "If the context does not contain the answer, say so plainly instead of "
    "inventing facts. Be concise and cite the concrete markers/ids you used. "
    "You may reply in the user's language (Vietnamese or English)."
)


def gemini_available() -> bool:
    """True when any chat-model key is configured. UI uses this to show status."""
    return bool(settings.gemini_api_key or os.getenv("OPENROUTER_API_KEY"))


def _to_contents(history: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Map chat history to google-genai `contents` turns.

    Roles: user -> "user", everything else (assistant/model) -> "model".
    """
    contents: list[dict[str, Any]] = []
    for msg in history:
        role = "user" if msg.get("role") == "user" else "model"
        text = msg.get("content", "")
        if not text:
            continue
        contents.append({"role": role, "parts": [{"text": text}]})
    return contents


def _grounding_prompt(memory_context: str, user_message: str) -> str:
    return (
        "Retrieved memory context for this turn:\n"
        "-------------------------------------\n"
        f"{memory_context.strip() or '(no memory retrieved)'}\n"
        "-------------------------------------\n\n"
        f"User message: {user_message}"
    )


def _openrouter_reply(
    memory_context: str,
    history: list[dict[str, str]],
    user_message: str,
    *,
    model: str | None = None,
) -> str:
    """OpenAI-compatible chat completion against OpenRouter (no extra SDK)."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing.")

    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_INSTRUCTION}]
    for msg in history:
        role = "user" if msg.get("role") == "user" else "assistant"
        text = msg.get("content", "")
        if text:
            messages.append({"role": role, "content": text})
    messages.append(
        {"role": "user", "content": _grounding_prompt(memory_context, user_message)}
    )

    model_name = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_name,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 800,
        },
        timeout=90,
    )
    response.raise_for_status()
    data = response.json()
    return (data["choices"][0]["message"]["content"] or "").strip()


def generate_reply(
    memory_context: str,
    history: list[dict[str, str]],
    user_message: str,
    *,
    model: str | None = None,
) -> str:
    """Generate a grounded assistant reply with Gemini or OpenRouter.

    Raises RuntimeError if no key, and lets SDK/network errors bubble up so the
    UI can surface them. `history` should include the latest user turn or not —
    `user_message` is appended as the final user turn regardless.
    """
    if settings.gemini_api_key:
        # Lazy import so the rest of the package works without google-genai
        # installed (tests, report generation, retrieval benchmarks never need it).
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        model_name = model or settings.gemini_model

        contents = _to_contents(history)
        contents.append(
            {"role": "user", "parts": [{"text": _grounding_prompt(memory_context, user_message)}]}
        )

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                max_output_tokens=800,
            ),
        )
        return (getattr(response, "text", "") or "").strip()

    if os.getenv("OPENROUTER_API_KEY"):
        return _openrouter_reply(memory_context, history, user_message, model=model)

    raise RuntimeError(
        "No chat-model key configured. Add GEMINI_API_KEY (Google AI Studio) "
        "or OPENROUTER_API_KEY to .env to enable chat replies."
    )
