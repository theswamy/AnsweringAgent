"""Runtime configuration, loaded from environment variables / .env.

Secrets (API keys, auth tokens) live here and are NEVER written to the database
or returned over the companion-app API.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Anthropic ---
    anthropic_api_key: str = ""
    # claude-opus-4-8 is the most capable default. For a live phone call you may
    # prefer claude-haiku-4-5, which lowers per-turn latency at some quality cost.
    # Switching the model is a deliberate choice — change it here if you want it.
    claude_model: str = "claude-opus-4-8"

    # --- Twilio (telephony provider that actually answers the forwarded call) ---
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    # The Twilio number your cell forwards to (E.164, e.g. +14155550123).
    twilio_phone_number: str = ""

    # --- App ---
    # Base URL where this server is reachable by Twilio (https, public).
    public_base_url: str = "http://localhost:8000"
    # Shared secret the iOS companion app sends in the X-API-Key header.
    app_api_key: str = "change-me-in-production"
    database_path: str = "answering_agent.db"

    # Max number of empty / no-input prompts before the agent gives up politely.
    max_no_input_retries: int = 2


@lru_cache
def get_settings() -> Settings:
    return Settings()
