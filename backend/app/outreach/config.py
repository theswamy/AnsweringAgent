"""Outreach-agent configuration, loaded from environment / .env.

Secrets (API tokens, OAuth creds) live here and are never written to the board
or logged. The operational cadence Sanjay specified is encoded as defaults:
initial emails go out **Mondays 16:00 IST, 25 companies per batch**, with
no-reply follow-ups at **+36 hours and +8 days**, then stop.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# The MicroVC Sourcing board is the System of Record.
DEFAULT_BOARD_ID = "18410878634"

# Board column ids (from get_board_info) the agent reads/writes.
COL_OUTREACH_STATUS = "color_mm2w2wv"
COL_STAGE = "text_mm2wcv77"
COL_LAST_ROUND_TYPE = "text_mm2whw"
COL_BEST_FOUNDER = "text_mm2ww997"
COL_FOUNDER_LINKEDIN = "link_mm2wccf8"
COL_SECTOR_TAG = "text_mm2wpqc2"        # labelled "Best Founder Domain"; holds a sector
COL_WEBSITE = "link_mm2w7w62"
COL_ONE_LINER = "long_text_mm2wzcyv"
COL_MICROVC_DROPDOWN = "dropdown_mm2wd7b0"  # unreliable; group title is authoritative


class OutreachSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="OUTREACH_", extra="ignore"
    )

    # --- Anthropic (drafting / classification) ---
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-4-8"

    # --- monday.com (System of Record) ---
    monday_api_token: str = ""
    monday_board_id: str = DEFAULT_BOARD_ID

    # --- Gmail (transport; dedicated address, used for nothing else) ---
    send_from_email: str = "sanjay.prime@primevp.in"
    sender_display_name: str = "Sanjay Swamy"
    gmail_oauth_json: str = ""          # path to OAuth client/token json

    # --- Scheduling ---
    calendly_url: str = ""

    # --- Cadence / volume (Sanjay's spec) ---
    send_weekday: int = 0               # Monday (Mon=0 .. Sun=6)
    send_hour_local: int = 16           # 16:00
    send_timezone: str = "Asia/Kolkata" # IST
    batch_size: int = 25                # companies per send batch
    followup_hours: tuple[int, ...] = (36, 24 * 8)  # +36h, then +8 days, then stop

    # Optional restriction of backing funds. Empty => no restriction (the board
    # is already scoped to Sanjay's target micro-VCs).
    target_funds: tuple[str, ...] = ()

    # Safety default: unreadable stage skews early on this board, so keep it.
    qualify_unknown_stage: bool = True


@lru_cache
def get_outreach_settings() -> OutreachSettings:
    return OutreachSettings()
