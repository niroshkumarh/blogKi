@echo off
REM Quick setup script for development (Windows)

echo Setting up Horizon Blog...

REM Check Python version
python --version
echo.

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
echo Dependencies installed

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit .env and add your Entra ID credentials
) else (
    echo .env file exists
)

REM Initialize database
if not exist "blogsite.db" (
    echo Initializing database...
    python init_db.py
    echo Database initialized
    
    echo Migrating existing posts...
    python migrate_posts.py
    echo Posts migrated
) else (
    echo Database exists
)

echo.
echo Setup complete!
echo.
echo To start the development server:
echo   venv\Scripts\activate.bat
echo   python app.py
echo.
echo Then visit: http://localhost:5000
pause


