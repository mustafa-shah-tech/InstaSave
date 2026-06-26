import os
from flask import Flask, render_template, request, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Required for browser status messages

# Automatically saves videos to your Windows Downloads folder
DOWNLOAD_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('video_url')
        if not url:
            flash('Please enter a valid URL!', 'danger')
            return render_template('index.html')

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            flash('Download completed! Check your Windows Downloads folder.', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
