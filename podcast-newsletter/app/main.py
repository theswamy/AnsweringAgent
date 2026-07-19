"""FastAPI app: the web control panel + JSON API, plus the daily scheduler.

Surfaces:
  • GET  /                      the config web UI (static single page)
  • /api/genres                 Apple genre catalogue for the topic picker
  • /api/topics                 list / add / toggle / remove topics
  • /api/shows                  list / add / remove followed shows
  • /api/shows/resolve          turn a URL / id / search term into a show to add
  • /api/run                    build + deliver today's issue right now
  • /api/newsletters            archive list + one issue's HTML
"""
from __future__ import annotations

import asyncio
import logging
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import db, podcasts
from .config import get_settings
from .runner import run_daily
from .scheduler import scheduler_loop

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("podcast_digest")

app = FastAPI(title="Podcast Digest")

_STATIC_DIR = __file__.rsplit("/", 2)[0] + "/static"


@app.on_event("startup")
async def _startup() -> None:
    db.init_db()
    # Fire-and-forget the daily scheduler inside this same process.
    asyncio.create_task(scheduler_loop())


# --------------------------------------------------------------------------- #
# Reference data                                                               #
# --------------------------------------------------------------------------- #

@app.get("/api/genres")
def genres() -> dict[str, int]:
    return podcasts.GENRES


# --------------------------------------------------------------------------- #
# Topics                                                                       #
# --------------------------------------------------------------------------- #

class TopicIn(BaseModel):
    name: str


@app.get("/api/topics")
def get_topics() -> list[dict]:
    return db.list_topics()


@app.post("/api/topics")
def add_topic(body: TopicIn) -> dict:
    genre_id = podcasts.GENRES.get(body.name)
    if genre_id is None:
        raise HTTPException(400, f"Unknown topic '{body.name}'. See /api/genres.")
    db.add_topic(body.name, genre_id)
    return {"ok": True}


@app.post("/api/topics/{topic_id}/toggle")
def toggle_topic(topic_id: int, enabled: bool = True) -> dict:
    db.set_topic_enabled(topic_id, enabled)
    return {"ok": True}


@app.delete("/api/topics/{topic_id}")
def delete_topic(topic_id: int) -> dict:
    db.remove_topic(topic_id)
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Followed shows                                                               #
# --------------------------------------------------------------------------- #

class ShowIn(BaseModel):
    # An Apple Podcasts URL, a numeric iTunes id, an RSS feed URL, or free text.
    query: str


@app.get("/api/shows")
def get_shows() -> list[dict]:
    return db.list_shows()


async def _resolve_show(query: str) -> podcasts.Podcast | None:
    query = query.strip()
    # Apple Podcasts URL → extract the id.../id123456789 segment.
    m = re.search(r"/id(\d+)", query)
    if m:
        return await podcasts.lookup(m.group(1), get_settings().country)
    if query.isdigit():
        return await podcasts.lookup(query, get_settings().country)
    if query.startswith("http"):
        return await podcasts.feed_meta(query)
    results = await podcasts.search(query, get_settings().country, limit=1)
    return results[0] if results else None


@app.post("/api/shows/resolve")
async def resolve_show(body: ShowIn) -> dict:
    """Preview what a query resolves to, without adding it."""
    show = await _resolve_show(body.query)
    if not show or not show.feed_url:
        raise HTTPException(404, "Couldn't find a podcast with a usable feed for that.")
    return {
        "title": show.title,
        "author": show.author,
        "feed_url": show.feed_url,
        "apple_url": show.apple_url,
        "artwork_url": show.artwork_url,
        "itunes_id": show.itunes_id,
    }


@app.post("/api/shows")
async def add_show(body: ShowIn) -> dict:
    show = await _resolve_show(body.query)
    if not show or not show.feed_url:
        raise HTTPException(404, "Couldn't find a podcast with a usable feed for that.")
    show_id = db.add_show(
        title=show.title,
        feed_url=show.feed_url,
        itunes_id=show.itunes_id,
        apple_url=show.apple_url,
        artwork_url=show.artwork_url,
    )
    return {"ok": True, "id": show_id, "title": show.title}


@app.delete("/api/shows/{show_id}")
def delete_show(show_id: int) -> dict:
    db.remove_show(show_id)
    return {"ok": True}


# --------------------------------------------------------------------------- #
# Run + archive                                                                #
# --------------------------------------------------------------------------- #

@app.post("/api/run")
async def run_now() -> dict:
    result = await run_daily()
    return {
        "newsletter_id": result.newsletter_id,
        "subject": result.subject,
        "deep_dives": result.deep_dives,
        "topics": result.topics,
        "delivery": result.delivery,
    }


@app.get("/api/newsletters")
def newsletters() -> list[dict]:
    return db.list_newsletters()


@app.get("/api/newsletters/{newsletter_id}", response_class=HTMLResponse)
def newsletter_html(newsletter_id: int) -> HTMLResponse:
    issue = db.get_newsletter(newsletter_id)
    if not issue:
        raise HTTPException(404, "No such newsletter.")
    return HTMLResponse(issue["html"])


# --------------------------------------------------------------------------- #
# Web UI                                                                       #
# --------------------------------------------------------------------------- #

@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(_STATIC_DIR + "/index.html")


app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
