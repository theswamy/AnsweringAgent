#!/usr/bin/env bash
# macOS/Linux launcher for the Podcast Digest control panel.
# On a Mac you can just double-click this file in Finder.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "First-time setup — installing (takes a minute)…"
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "──────────────────────────────────────────────"
echo "  Podcast Digest is running."
echo "  Open your browser to:  http://localhost:8000"
echo "  (Close this window to stop it.)"
echo "──────────────────────────────────────────────"
echo ""

# Open the browser automatically once the server is up.
( sleep 2; command -v open >/dev/null 2>&1 && open http://localhost:8000 ) &
exec uvicorn app.main:app --host 127.0.0.1 --port 8000
