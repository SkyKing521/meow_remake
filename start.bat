@echo off
echo Starting Meow Voice Chat Application...

REM Start the server
start cmd /k "python main.py"

REM Wait a moment for the server to start
timeout /t 5

REM Start the client с правильным HOST
set HOST=0.0.0.0
set PORT=3000
start cmd /k "set HOST=%HOST% && set PORT=%PORT% && npm start"

echo Applications started!
echo Server is running at http://26.34.237.219:8000
echo Client is running at http://26.34.237.219:3000 