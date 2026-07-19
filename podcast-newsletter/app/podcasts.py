"""Podcast sourcing: Apple Podcasts charts + iTunes lookup/search + RSS feeds.

Why Apple? The iTunes/Apple Podcasts APIs are free, need no key, and expose both
the per-topic "top podcasts" charts and each show's RSS feed URL. Apple does not
publish numeric star ratings through a public API, so the genre *charts* — which
Apple ranks largely by popularity and ratings — are the best available proxy for
"top rated on this topic". Once we have a feed URL, episodes come straight from
the show's own RSS (title, show notes, audio, publish date, episode web link).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import feedparser
import httpx

# Apple Podcasts genre ids. These are the topics you can pull a top-N chart for.
GENRES: dict[str, int] = {
    "Arts": 1301,
    "Business": 1321,
    "Comedy": 1303,
    "Education": 1304,
    "Fiction": 1483,
    "Government": 1511,
    "Health & Fitness": 1512,
    "History": 1487,
    "Kids & Family": 1305,
    "Leisure": 1502,
    "Music": 1310,
    "News": 1489,
    "Religion & Spirituality": 1314,
    "Science": 1533,
    "Society & Culture": 1324,
    "Sports": 1545,
    "Technology": 1318,
    "True Crime": 1488,
    "TV & Film": 1309,
}

_USER_AGENT = "PodcastDigest/1.0 (+https://github.com/theswamy/answeringagent)"
_TIMEOUT = httpx.Timeout(20.0)


@dataclass
class Podcast:
    """A show, identified by its iTunes collection id where we have one."""

    itunes_id: str | None
    title: str
    author: str = ""
    feed_url: str | None = None
    apple_url: str | None = None
    artwork_url: str | None = None
    description: str = ""


@dataclass
class Episode:
    guid: str
    title: str
    summary: str  # show notes / description as published in the feed
    published: datetime | None
    audio_url: str | None = None
    link: str | None = None  # episode web page, if the feed provides one
    duration: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


async def _get_json(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    resp = await client.get(url, headers={"User-Agent": _USER_AGENT})
    resp.raise_for_status()
    # Apple serves the RSS-chart JSON as text/javascript; ask httpx to parse anyway.
    return resp.json()


async def top_podcasts(genre_id: int, country: str, limit: int) -> list[Podcast]:
    """The current top chart for a genre, newest Apple ranking first.

    The chart entries carry the collection id but not the feed URL, so callers who
    need episodes should pass the results through :func:`hydrate` (or call
    :func:`lookup` per id) to fill in ``feed_url``.
    """
    url = (
        f"https://itunes.apple.com/{country}/rss/toppodcasts/"
        f"limit={limit}/genre={genre_id}/json"
    )
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        data = await _get_json(client, url)

    entries = (data.get("feed") or {}).get("entry") or []
    # Apple returns a bare object (not a list) when limit resolves to one entry.
    if isinstance(entries, dict):
        entries = [entries]

    shows: list[Podcast] = []
    for e in entries:
        attrs = (e.get("id") or {}).get("attributes") or {}
        itunes_id = attrs.get("im:id")
        title = (e.get("im:name") or {}).get("label", "").strip()
        author = (e.get("im:artist") or {}).get("label", "").strip()
        apple_url = attrs.get("href") or (e.get("id") or {}).get("label")
        images = e.get("im:image") or []
        artwork = images[-1].get("label") if images else None
        summary = (e.get("summary") or {}).get("label", "")
        if not (itunes_id and title):
            continue
        shows.append(
            Podcast(
                itunes_id=itunes_id,
                title=title,
                author=author,
                apple_url=apple_url,
                artwork_url=artwork,
                description=summary,
            )
        )
    return shows


async def lookup(itunes_id: str, country: str = "us") -> Podcast | None:
    """Resolve an iTunes collection id to full metadata, including the feed URL."""
    url = f"https://itunes.apple.com/lookup?id={itunes_id}&entity=podcast&country={country}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        data = await _get_json(client, url)
    results = data.get("results") or []
    if not results:
        return None
    return _podcast_from_itunes(results[0])


async def search(term: str, country: str, limit: int = 5) -> list[Podcast]:
    """Search the podcast catalogue by free text (title, host, keywords)."""
    # Build the query safely rather than hand-encoding the term.
    url = str(
        httpx.URL(
            "https://itunes.apple.com/search",
            params={
                "term": term,
                "entity": "podcast",
                "limit": limit,
                "country": country,
            },
        )
    )
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        data = await _get_json(client, url)
    return [_podcast_from_itunes(r) for r in (data.get("results") or [])]


def _podcast_from_itunes(r: dict[str, Any]) -> Podcast:
    return Podcast(
        itunes_id=str(r.get("collectionId")) if r.get("collectionId") else None,
        title=r.get("collectionName") or r.get("trackName") or "Untitled",
        author=r.get("artistName", ""),
        feed_url=r.get("feedUrl"),
        apple_url=r.get("collectionViewUrl") or r.get("trackViewUrl"),
        artwork_url=r.get("artworkUrl600") or r.get("artworkUrl100"),
        description=r.get("collectionName", ""),
    )


async def hydrate(shows: list[Podcast], country: str) -> list[Podcast]:
    """Fill in missing ``feed_url``/artwork for chart entries via iTunes lookup."""
    for show in shows:
        if show.feed_url or not show.itunes_id:
            continue
        full = await lookup(show.itunes_id, country)
        if full:
            show.feed_url = full.feed_url
            show.author = show.author or full.author
            show.artwork_url = show.artwork_url or full.artwork_url
    return shows


def _parsed_time_to_dt(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromtimestamp(time.mktime(value), tz=timezone.utc)
    except (OverflowError, ValueError, TypeError):
        return None


def parse_feed(raw: bytes | str) -> list[Episode]:
    """Parse a podcast RSS document (bytes or text) into episodes, newest first."""
    parsed = feedparser.parse(raw)
    episodes: list[Episode] = []
    for item in parsed.entries:
        audio = None
        for link in item.get("links", []):
            if link.get("rel") == "enclosure" or link.get("type", "").startswith("audio"):
                audio = link.get("href")
                break
        summary = item.get("summary", "") or item.get("subtitle", "")
        episodes.append(
            Episode(
                guid=item.get("id") or item.get("link") or item.get("title", ""),
                title=item.get("title", "Untitled episode"),
                summary=summary,
                published=_parsed_time_to_dt(item.get("published_parsed")),
                audio_url=audio,
                link=item.get("link"),
                duration=str(item.get("itunes_duration", "")),
            )
        )
    episodes.sort(key=lambda e: e.published or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return episodes


async def feed_meta(feed_url: str) -> Podcast | None:
    """Read a show's title/artwork straight from its RSS (for user-added feed URLs)."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(feed_url, headers={"User-Agent": _USER_AGENT})
            resp.raise_for_status()
    except httpx.HTTPError:
        return None
    parsed = feedparser.parse(resp.content)
    feed = parsed.get("feed") or {}
    title = feed.get("title")
    if not title:
        return None
    image = (feed.get("image") or {}).get("href")
    return Podcast(
        itunes_id=None,
        title=title,
        author=feed.get("author", ""),
        feed_url=feed_url,
        apple_url=feed.get("link"),
        artwork_url=image,
        description=feed.get("subtitle", ""),
    )


async def fetch_episodes(feed_url: str) -> list[Episode]:
    """Download and parse a show's feed. Returns [] if the feed can't be read."""
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(feed_url, headers={"User-Agent": _USER_AGENT})
            resp.raise_for_status()
            return parse_feed(resp.content)
    except (httpx.HTTPError, ValueError):
        return []
