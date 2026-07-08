import os
import re
import secrets
from urllib.parse import urlparse

from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(24))

DOWNLOAD_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def strip_ansi(text: str) -> str:
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url', '').strip()

    if not is_valid_url(url):
        return jsonify({'success': False,
                        'message': 'Invalid URL. Must start with http:// or https://'})

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return jsonify({'success': True,
                        'message': 'Downloaded! Check your Downloads folder.'})
    except Exception as e:
        return jsonify({'success': False, 'message': strip_ansi(str(e))})


if __name__ == '__main__':
    app.run(debug=False)
