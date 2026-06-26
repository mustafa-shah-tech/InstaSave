import os
import secrets
import json
from urllib.parse import urlparse

from flask import Flask, render_template, request, flash, Response, stream_with_context
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

    def event_stream(url):
        # --- Validate URL ---
        if not is_valid_url(url):
            payload = json.dumps({'type': 'error', 'message': 'Invalid URL. Please enter a valid http:// or https:// link.'})
            yield f'data: {payload}\n\n'
            return

        # --- Progress hook passed to yt-dlp ---
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                try:
                    percent = float(percent_str)
                except ValueError:
                    percent = 0.0
                payload = json.dumps({'type': 'progress', 'percent': round(percent, 1)})
                yield f'data: {payload}\n\n'

        # yt-dlp doesn't natively support generator-based hooks, so we use a list
        # to collect events and yield them outside the hook.
        events = []

        def hook(d):
            if d['status'] == 'downloading':
                percent_str = d.get('_percent_str', '0%').strip().replace('%', '')
                try:
                    percent = float(percent_str)
                except ValueError:
                    percent = 0.0
                events.append({'type': 'progress', 'percent': round(percent, 1)})
            elif d['status'] == 'finished':
                events.append({'type': 'progress', 'percent': 100.0})

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [hook],
            # Suppress console output; progress comes via SSE
            'quiet': True,
            'no_warnings': True,
        }

        # Yield an initial "started" event so the UI shows the bar immediately
        yield f'data: {json.dumps({"type": "progress", "percent": 0})}\n\n'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                # Flush any remaining events collected by the hook
                for ev in events:
                    yield f'data: {json.dumps(ev)}\n\n'
            payload = json.dumps({'type': 'done', 'message': 'Download completed! Check your Downloads folder.'})
            yield f'data: {payload}\n\n'
        except Exception as e:
            payload = json.dumps({'type': 'error', 'message': str(e)})
            yield f'data: {payload}\n\n'

    return Response(
        stream_with_context(event_stream(url)),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',   # Disable nginx buffering if behind a proxy
        }
    )


if __name__ == '__main__':
    # Set debug=True only during local development; never in production.
    app.run(debug=False)
