@echo off
title LinkVault Server
echo =========================================
echo       Starting LinkVault Application     
echo =========================================
echo.

IF NOT EXIST "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found in 'venv' folder!
    echo Please make sure you have installed the requirements.
    pause
    exit /b
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Opening your web browser...
:: Wait 2 seconds before opening browser to give the server a moment to start
timeout /t 2 /nobreak > nul
start http://127.0.0.1:5000

echo [3/3] Starting the Flask server...
echo.
python app.py

pause
