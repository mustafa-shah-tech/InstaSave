import os
import secrets
import json
from urllib.parse import urlparse
import queue
import threading
import re

from flask import Flask, render_template, request, Response, stream_with_context
import yt_dlp

app = Flask(__name__)
# Load secret key from environment variable; fall back to a random key per process start.
# Set the SECRET_KEY env variable in production for session persistence across restarts.
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24))

# Saves videos to the current user's Windows Downloads folder
DOWNLOAD_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')


def is_valid_url(url: str) -> bool:
    """Return True only for absolute http/https URLs."""
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/download', methods=['GET'])
def download():
    """
    Server-Sent Events endpoint.
    The browser opens GET /download?url=<encoded_url> via EventSource.
    We stream back 'data: <json>\\n\\n' events until done or error.
    """
    url = request.args.get('url', '').strip()
    cookies_path = request.args.get('cookies_path', '').strip()

    def event_stream(url, cookies_path):
        # --- Validate URL ---
        if not is_valid_url(url):
            payload = json.dumps({'type': 'error', 'message': 'Invalid URL. Please enter a valid http:// or https:// link.'})
            yield f'data: {payload}\n\n'
            return

        q = queue.Queue()
        SENTINEL = object()

        def hook(d):
            if d['status'] == 'downloading':
                pct_str = d.get('_percent_str', '0%').strip().replace('%','')
                try:
                    pct = float(pct_str)
                except ValueError:
                    pct = 0.0
                q.put({'type': 'progress', 'percent': round(pct, 1)})
            elif d['status'] == 'finished':
                q.put({'type': 'progress', 'percent': 100.0})

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'progress_hooks': [hook],
            # Suppress console output; progress comes via SSE
            'quiet': True,
            'no_warnings': True,
        }

        if cookies_path and os.path.isfile(cookies_path):
            ydl_opts['cookiefile'] = cookies_path

        def run_download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                q.put({'type': 'done', 'message': 'Download completed! Check your Downloads folder.'})
            except Exception as e:
                q.put({'type': 'error', 'message': strip_ansi(str(e))})
            finally:
                q.put(SENTINEL)

        t = threading.Thread(target=run_download, daemon=True)
        t.start()

        # Yield an initial "started" event so the UI shows the bar immediately
        yield f'data: {json.dumps({"type": "progress", "percent": 0})}\n\n'

        while True:
            item = q.get()
            if item is SENTINEL:
                break
            yield f'data: {json.dumps(item)}\n\n'

    return Response(
        stream_with_context(event_stream(url, cookies_path)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',   # Disable nginx buffering if behind a proxy
        }
    )


if __name__ == '__main__':
    # Set debug=True only during local development; never in production.
    app.run(debug=False)
