# 🎬 InstaSave

A sleek, premium, and lightning-fast local video downloader web application. Built with a stunning dark-mode glassmorphism interface, InstaSave allows you to download videos from over 1,000+ supported websites directly to your computer.

---

## ✨ Features

- **Universal Support**: Powered by `yt-dlp`, supporting downloads from YouTube, Instagram, TikTok, Twitter/X, and 1000+ other platforms.
- **Premium UI**: A beautiful, responsive, glassmorphic dark-mode interface with smooth animations and custom styling.
- **Real-Time Progress**: Watch the download progress directly in your terminal/command prompt while the video downloads.
- **One-Click Start**: Includes a handy `.bat` script for Windows users to launch the server and open the browser automatically in a single click.
- **Local & Private**: No shady third-party sites, no ads, no trackers. Everything runs locally on your machine.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:

1. **Python 3.8+** (Make sure to check "Add Python to PATH" during installation)
2. **FFmpeg** (Highly recommended, required by `yt-dlp` for merging high-quality video and audio streams)

---

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mustafa-shah-tech/InstaSave.git
   cd InstaSave
   ```

2. **Install the required Python packages:**
   ```bash
   pip install flask yt-dlp
   ```

---

## 💻 Usage

### For Windows Users (The Easy Way)
Simply double-click the **`Start InstaSave.bat`** file. 
It will automatically start the background server and open the application in your default web browser.

### Manual Start (Mac / Linux / Windows)
1. Open your terminal in the project directory.
2. Run the application:
   ```bash
   python app.py
   ```
3. Open your web browser and navigate to: `http://127.0.0.1:5000`

---

## 📸 How it Works

1. Paste your desired video URL into the input field.
2. Click **Download Video**.
3. Check your terminal window to see the live download progress percentage.
4. Once completed, your video will be saved in your system's default `Downloads` folder!

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
