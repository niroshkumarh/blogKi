@echo off
REM Wide Angle Blog - Docker Quick Start Script (Windows)

echo.
echo 🐳 Wide Angle Blog - Docker Setup
echo ==================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found!
    echo.
    echo Creating .env from example...
    copy env.docker.example .env
    echo.
    echo ✅ Created .env file
    echo.
    echo ⚠️  IMPORTANT: Edit .env and update:
    echo    - CLIENT_SECRET ^(from Azure Portal^)
    echo    - ADMIN_EMAILS ^(your email address^)
    echo    - SECRET_KEY ^(random string^)
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✅ Found .env file
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running!
    echo    Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running
echo.

REM Build and start containers
echo 🏗️  Building and starting containers...
echo.

docker-compose up --build -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Containers started successfully!
    echo.
    echo 📊 Container Status:
    docker-compose ps
    echo.
    echo 🎉 Your blog is ready!
    echo.
    echo    🌐 Blog: http://localhost:4343
    echo    📊 Database: localhost:5432
    echo.
    echo 📝 View logs:
    echo    docker-compose logs -f
    echo.
    echo 🛑 Stop containers:
    echo    docker-compose stop
    echo.
) else (
    echo.
    echo ❌ Failed to start containers
    echo    Check the logs: docker-compose logs
    pause
    exit /b 1
)

pause

