"""Turn an episode's raw show notes into a tight, useful summary with Claude.

We summarize from the feed's show notes / description rather than transcribing the
audio: it needs no audio pipeline, is fast and cheap to run daily, and show notes
are what publishers write to describe the episode. The prompt tells Claude to be
honest when the notes are thin instead of inventing content.
"""
from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from typing import Any

import anthropic

from .config import get_settings
from .podcasts import Episode

_SUMMARY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "A 3-5 sentence summary of what this episode covers, in plain, "
            "engaging prose. If the show notes are too sparse to summarize the actual "
            "content, say what the episode is about at a high level and note that details "
            "are limited — never fabricate specifics, guests, or claims.",
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "2-4 concrete takeaways or topics, each a short phrase. Empty if "
            "the notes don't support any.",
        },
        "why_listen": {
            "type": "string",
            "description": "One sentence on who would get the most out of this episode.",
        },
    },
    "required": ["summary", "key_points", "why_listen"],
    "additionalProperties": False,
}


@dataclass
class EpisodeSummary:
    summary: str
    key_points: list[str]
    why_listen: str


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _fallback(episode: Episode) -> EpisodeSummary:
    """Used when no Anthropic key is configured — echo the cleaned show notes."""
    notes = _strip_html(episode.summary)
    trimmed = notes[:600] + ("…" if len(notes) > 600 else "")
    return EpisodeSummary(
        summary=trimmed or "No show notes were provided for this episode.",
        key_points=[],
        why_listen="",
    )


def summarize_episode(podcast_title: str, episode: Episode) -> EpisodeSummary:
    """Summarize one episode. Falls back to trimmed show notes without an API key."""
    settings = get_settings()
    if not settings.anthropic_api_key:
        return _fallback(episode)

    notes = _strip_html(episode.summary)[:6000]
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=700,
        system=(
            "You write concise, trustworthy summaries of podcast episodes for a daily "
            "email digest. Work only from the show notes provided. Be specific where the "
            "notes allow and honest where they don't."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Podcast: {podcast_title}\n"
                    f"Episode: {episode.title}\n"
                    f"Published: {episode.published.date() if episode.published else 'unknown'}\n\n"
                    f"Show notes:\n{notes or '(none provided)'}"
                ),
            }
        ],
        output_config={"format": {"type": "json_schema", "schema": _SUMMARY_SCHEMA}},
    )
    text = next((b.text for b in response.content if b.type == "text"), "{}")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _fallback(episode)
    return EpisodeSummary(
        summary=data.get("summary", "").strip() or _fallback(episode).summary,
        key_points=[p for p in data.get("key_points", []) if p][:4],
        why_listen=data.get("why_listen", "").strip(),
    )


def one_liner(podcast_title: str, episode: Episode) -> str:
    """A single-sentence take on an episode, for the top-list rows."""
    settings = get_settings()
    notes = _strip_html(episode.summary)
    if not settings.anthropic_api_key:
        return (notes[:160] + "…") if len(notes) > 160 else notes
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=120,
        system="Reply with exactly one plain sentence. No preamble.",
        messages=[
            {
                "role": "user",
                "content": (
                    f"In one sentence, what is this podcast episode about? "
                    f"Podcast: {podcast_title}. Episode: {episode.title}. "
                    f"Notes: {notes[:1500] or '(none)'}"
                ),
            }
        ],
    )
    return next((b.text for b in response.content if b.type == "text"), "").strip()
