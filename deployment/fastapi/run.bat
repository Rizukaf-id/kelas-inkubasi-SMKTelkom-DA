@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
  echo Creating virtual environment...
  py -3 -m venv .venv
)

echo Activating environment...
call .\.venv\Scripts\activate.bat

echo Installing requirements (first time may take a while)...
pip install -r requirements.txt

echo Starting server on http://127.0.0.1:8000/
uvicorn app:app --host 127.0.0.1 --port 8000 --reload

endlocal
