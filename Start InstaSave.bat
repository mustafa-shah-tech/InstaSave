@echo off
echo Starting InstaSave...
echo Please wait a moment while the server starts...

:: Open the default web browser to the local server
start http://127.0.0.1:5000

:: Start the Python Flask app
python app.py

pause
