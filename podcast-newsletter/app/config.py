"""Runtime configuration, loaded from environment variables / .env.

Secrets (the Anthropic key, SMTP password) live here and are never written to the
database or served over the web UI.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Anthropic (writes the summaries) ---
    anthropic_api_key: str = ""
    # claude-opus-4-8 is the most capable default. claude-haiku-4-5 is cheaper and
    # perfectly good for short episode summaries if you send this daily at scale.
    claude_model: str = "claude-opus-4-8"

    # --- Email delivery (SMTP works with Gmail app passwords, SendGrid, SES, ...) ---
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True  # STARTTLS on port 587; set false + port 465 for SSL
    email_from: str = ""
    # Where the daily newsletter is sent. Pre-filled for the owner of this deployment.
    email_to: str = "sanjay@primevp.in"

    # If true (or if SMTP is not configured), the newsletter is written to ./outbox/
    # as an .html file instead of being emailed. Great for local development.
    dry_run: bool = False

    # --- Sourcing ---
    # Apple Podcasts storefront country. Charts and search are region-specific.
    country: str = "us"
    # How many "top" podcasts to list per topic.
    top_n: int = 10
    # Also have Claude write a one-line take on each top-list podcast's latest
    # episode. Off by default to keep daily token cost low; the deep "episode of
    # the day" summary is always written.
    summarize_top_list: bool = False

    # --- Schedule ---
    # Local hour (0-23) at which the daily send runs when the scheduler is on.
    send_hour: int = 7
    # IANA timezone the send_hour is interpreted in.
    timezone: str = "Asia/Kolkata"

    # --- Storage ---
    database_path: str = "podcast_digest.db"


@lru_cache
def get_settings() -> Settings:
    return Settings()
