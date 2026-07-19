"""Deliver the newsletter.

Real send is plain SMTP so it works with anything: a Gmail app password, SendGrid,
Amazon SES, Postmark, your own mail server. If SMTP isn't configured (or DRY_RUN is
set) the issue is written to ./outbox/ as an .html file instead — handy for local
development and for previewing before you wire up mail.
"""
from __future__ import annotations

import os
import smtplib
import ssl
from datetime import date
from email.message import EmailMessage
from email.utils import formataddr

from . import db
from .config import get_settings

_OUTBOX = "outbox"

# The email/SMTP fields a user can set in the control panel. For each, a value
# saved in the UI (DB) wins; otherwise the matching environment variable is used;
# otherwise the built-in default. Locally the DB holds the values and env is
# empty; in the cloud/CI env holds them and the DB is empty — so the two never
# collide and secrets stay in env there.
def email_config() -> dict:
    s = get_settings()
    ui = db.get_settings_map()

    def pick(key: str, env_value: str, default: str = "") -> str:
        return (ui.get(key) or env_value or default).strip()

    port_raw = ui.get("smtp_port") or str(s.smtp_port or "") or "587"
    try:
        port = int(port_raw)
    except ValueError:
        port = 587
    use_tls = ui.get("smtp_use_tls")
    return {
        "smtp_host": pick("smtp_host", s.smtp_host),
        "smtp_port": port,
        "smtp_username": pick("smtp_username", s.smtp_username),
        "smtp_password": pick("smtp_password", s.smtp_password),
        "smtp_use_tls": (use_tls == "true") if use_tls is not None else s.smtp_use_tls,
        "email_from": pick("email_from", s.email_from),
    }


def _recipients() -> list[str]:
    """The current recipient list (managed in the web UI), else the config seed."""
    people = db.recipient_emails()
    if people:
        return people
    return [get_settings().email_to] if get_settings().email_to else []


def deliver(subject: str, html: str, for_date: date | None = None) -> str:
    """Send (or, in dry-run, save) the newsletter. Returns a human-readable status."""
    s = get_settings()
    cfg = email_config()
    for_date = for_date or date.today()
    recipients = _recipients()

    if s.dry_run or not (cfg["smtp_host"] and cfg["email_from"]) or not recipients:
        os.makedirs(_OUTBOX, exist_ok=True)
        path = os.path.join(_OUTBOX, f"digest-{for_date.isoformat()}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        if s.dry_run:
            reason = "DRY_RUN set"
        elif not recipients:
            reason = "no recipients configured"
        else:
            reason = "SMTP not configured"
        return f"Saved to {path} ({reason}) — not emailed."

    from_addr = formataddr(("Podcast Digest", cfg["email_from"]))
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    # The list is addressed to the sending account; individual recipients go on
    # Bcc so nobody sees anyone else's address as the team grows.
    msg["To"] = from_addr
    msg["Bcc"] = ", ".join(recipients)
    msg.set_content(
        "Your Podcast Digest is best viewed as HTML. If you're seeing this, your "
        "mail client can't render HTML email."
    )
    msg.add_alternative(html, subtype="html")

    _transmit(cfg, msg)
    n = len(recipients)
    return f"Emailed to {n} recipient{'s' if n != 1 else ''}."


def _transmit(cfg: dict, msg: EmailMessage) -> None:
    if cfg["smtp_port"] == 465:
        with smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"], context=ssl.create_default_context()) as srv:
            _login_and_send(srv, cfg, msg)
    else:
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as srv:
            if cfg["smtp_use_tls"]:
                srv.starttls(context=ssl.create_default_context())
            _login_and_send(srv, cfg, msg)


def _login_and_send(srv: smtplib.SMTP, cfg: dict, msg: EmailMessage) -> None:
    if cfg["smtp_username"]:
        srv.login(cfg["smtp_username"], cfg["smtp_password"])
    srv.send_message(msg)


def send_test() -> str:
    """Send a tiny email to the sender itself to verify the SMTP settings.

    Raises on failure so the UI can surface the exact SMTP error. Deliberately
    sends only to the sending account, never to the recipient list.
    """
    cfg = email_config()
    if not (cfg["smtp_host"] and cfg["email_from"]):
        raise ValueError("Set the sender address and SMTP host first.")
    from_addr = formataddr(("Podcast Digest", cfg["email_from"]))
    msg = EmailMessage()
    msg["Subject"] = "Podcast Digest — test email ✅"
    msg["From"] = from_addr
    msg["To"] = cfg["email_from"]
    msg.set_content("If you can read this, your Podcast Digest email settings are working.")
    _transmit(cfg, msg)
    return f"Test email sent to {cfg['email_from']}. Check that inbox."
