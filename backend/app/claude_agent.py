"""The brain of the answering machine.

Given the conversation so far (what the caller has said and what the agent has
replied), this asks Claude for the next thing to say and whether to hang up,
plus structured facts extracted from the call (caller name, intent, callback
details, whether the caller is itself an automated system).

We use structured outputs so every turn returns a predictable JSON shape. Thinking
is left off deliberately — a phone call is latency-sensitive and an answering-machine
turn is simple, so we trade a little depth for a faster reply.
"""
from __future__ import annotations

import json
from typing import Any

import anthropic

from .config import get_settings

# The JSON contract for every turn. additionalProperties:false + required is
# needed for structured outputs.
_TURN_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "speech": {
            "type": "string",
            "description": "What the agent should say next, spoken aloud to the caller. "
            "One or two short sentences — this is a phone call.",
        },
        "should_end": {
            "type": "boolean",
            "description": "True when the call is complete and the agent should say "
            "goodbye and hang up after this line.",
        },
        "caller_name": {
            "type": ["string", "null"],
            "description": "The caller's name once known, else null.",
        },
        "intent": {
            "type": ["string", "null"],
            "description": "A brief phrase describing what the caller wants to convey, else null.",
        },
        "callback_requested": {"type": "boolean"},
        "callback_number": {
            "type": ["string", "null"],
            "description": "Phone number to call back on, if the caller gave one.",
        },
        "callback_time": {
            "type": ["string", "null"],
            "description": "Preferred callback date/time as the caller stated it, if any.",
        },
        "is_automated": {
            "type": "boolean",
            "description": "True if the caller appears to be an IVR menu, a robocall, or "
            "another automated agent rather than a person.",
        },
    },
    "required": [
        "speech", "should_end", "caller_name", "intent",
        "callback_requested", "callback_number", "callback_time", "is_automated",
    ],
    "additionalProperties": False,
}


def _system_prompt(user_name: str, agent_defaults: str) -> str:
    return f"""You are the personal phone-answering agent for {user_name}. {user_name} \
is unavailable, so you are taking the call on their behalf — a smart answering machine.

Your job, in order:
1. Find out who is calling (you have already greeted them and asked who is speaking).
2. Your FIRST reply must ask what they would like to convey to {user_name}.
3. Capture their message clearly and confirm you have it.
4. If they want a callback, collect a convenient date/time AND a callback number.
5. Politely wrap up and end the call once you have what you need.

Style — this is a live phone call, so:
- Keep every spoken line to one or two short, natural sentences. Be warm but crisp.
- Do not ramble, do not over-apologise, do not invent information about {user_name}.
- You do not know {user_name}'s schedule, location, or personal details — never share any.
- If the caller is rude or refuses to identify themselves, stay polite and take whatever message you can, then end.

Handling automated callers / IVRs / other AI agents:
{agent_defaults}
When you detect such a caller, set is_automated to true and follow the guidance above.

Set should_end to true on the final line (a brief goodbye). Always fill the structured
fields with the best information you have so far; use null when something is not yet known."""


def advance_conversation(
    history: list[dict[str, str]],
    user_name: str,
    agent_defaults: str,
) -> dict[str, Any]:
    """Produce the agent's next turn.

    `history` is the ordered transcript: items are {"role": "caller"|"agent", "text": ...}.
    The most recent caller utterance should be last.
    """
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    messages = [
        {
            "role": "assistant" if t["role"] == "agent" else "user",
            "content": t["text"],
        }
        for t in history
    ]

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=600,
        system=_system_prompt(user_name, agent_defaults),
        messages=messages,
        output_config={"format": {"type": "json_schema", "schema": _TURN_SCHEMA}},
    )

    text = next((b.text for b in response.content if b.type == "text"), "{}")
    data: dict[str, Any] = json.loads(text)
    # Guard against an empty/whitespace utterance breaking the TwiML <Say>.
    if not (data.get("speech") or "").strip():
        data["speech"] = "Thank you. I'll pass your message along. Goodbye."
        data["should_end"] = True
    return data


def summarize_call(transcript: str, user_name: str) -> str:
    """A one-paragraph summary to store and to text to the owner."""
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=300,
        system=(
            f"Summarize this phone call for {user_name}, who missed it. Lead with who "
            "called and what they wanted in one sentence, then any callback request "
            "(time + number) and action needed. Be factual and concise — 2-4 sentences."
        ),
        messages=[{"role": "user", "content": transcript or "(no conversation captured)"}],
    )
    return next((b.text for b in response.content if b.type == "text"), "").strip()
