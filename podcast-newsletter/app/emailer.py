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


def _smtp_configured() -> bool:
    s = get_settings()
    return bool(s.smtp_host and s.email_from)


def _recipients() -> list[str]:
    """The current recipient list (managed in the web UI), else the config seed."""
    people = db.recipient_emails()
    if people:
        return people
    return [get_settings().email_to] if get_settings().email_to else []


def deliver(subject: str, html: str, for_date: date | None = None) -> str:
    """Send (or, in dry-run, save) the newsletter. Returns a human-readable status."""
    s = get_settings()
    for_date = for_date or date.today()
    recipients = _recipients()

    if s.dry_run or not _smtp_configured() or not recipients:
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

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr(("Podcast Digest", s.email_from))
    # The list is addressed to the sending account; individual recipients go on
    # Bcc so nobody sees anyone else's address as the team grows.
    msg["To"] = formataddr(("Podcast Digest", s.email_from))
    msg["Bcc"] = ", ".join(recipients)
    msg.set_content(
        "Your Podcast Digest is best viewed as HTML. If you're seeing this, your "
        "mail client can't render HTML email."
    )
    msg.add_alternative(html, subtype="html")

    if s.smtp_port == 465:
        with smtplib.SMTP_SSL(s.smtp_host, s.smtp_port, context=ssl.create_default_context()) as srv:
            _login_and_send(srv, s, msg)
    else:
        with smtplib.SMTP(s.smtp_host, s.smtp_port) as srv:
            if s.smtp_use_tls:
                srv.starttls(context=ssl.create_default_context())
            _login_and_send(srv, s, msg)

    n = len(recipients)
    return f"Emailed to {n} recipient{'s' if n != 1 else ''}."


def _login_and_send(srv: smtplib.SMTP, s, msg: EmailMessage) -> None:
    if s.smtp_username:
        srv.login(s.smtp_username, s.smtp_password)
    srv.send_message(msg)
