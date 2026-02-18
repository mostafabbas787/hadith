@echo off
echo ========================================
echo   Enhanced Hadith Video Generator
echo   Starting with Performance Optimizations
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Check if requirements are installed
if not exist "venv\Lib\site-packages\flask\" (
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements
        pause
        exit /b 1
    )
)

:: Ensure all directories exist
if not exist "temp\" mkdir temp
if not exist "outputs\" mkdir outputs
if not exist "static\fonts\" mkdir static\fonts

:: Start the application
echo [INFO] Starting Enhanced Hadith Video Generator...
echo.
echo ========================================
echo   Server Status:
echo   - Performance Manager: ENABLED
echo   - Async Processing: ENABLED  
echo   - KIE API: CONFIGURED
echo   - Caching: ENABLED
echo ========================================
echo.
echo [INFO] Application will be available at:
echo         http://localhost:5000
echo.
echo [INFO] Press Ctrl+C to stop the server
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application crashed or failed to start
    echo Check the error messages above for details
    echo.
    pause
)

echo.
echo [INFO] Enhanced Hadith Video Generator stopped
pause