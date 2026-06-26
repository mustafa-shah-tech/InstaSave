import yt_dlp

def download_youtube_video(video_url):
    # Configuration options for the downloader
    ydl_opts = {
        'format': 'best',  # Downloads the best available quality single file
        'outtmpl': '%(title)s.%(ext)s',  # Saves the video with its original title
    }
    
    try:
        print("Starting download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Paste your YouTube link here
url = input("Enter the YouTube video URL: ")
download_youtube_video(url)
