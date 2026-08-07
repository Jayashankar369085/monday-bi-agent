@echo off
REM Skylark Drones BI Agent - Local Development Startup Script (Windows)
REM Usage: start-dev.bat

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo     Skylark Drones BI Agent - Local Development Setup
echo ============================================================
echo.

REM Check for Docker
echo Checking for Docker...
docker --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
echo [OK] Docker is installed

REM Check for Docker Compose
echo Checking for Docker Compose...
docker-compose --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Desktop which includes Compose
    pause
    exit /b 1
)
echo [OK] Docker Compose is installed

REM Check for .env file
echo.
echo Checking environment configuration...
if not exist "backend\.env" (
    echo Creating .env file from template...
    copy backend\.env.example backend\.env
    echo.
    echo [WARNING] Please update backend\.env with your API keys:
    echo   - MONDAY_API_TOKEN=your_monday_api_token
    echo   - OPENAI_API_KEY=your_openai_api_key
    echo.
    set /p continue="Continue after updating .env? (y/n): "
    if /i not "!continue!"=="y" exit /b 1
)
echo [OK] .env file exists

REM Build services
echo.
echo Building Docker images...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Build failed
    pause
    exit /b 1
)

REM Start services
echo.
echo Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)

REM Wait for services
echo.
echo Waiting for services to start...
timeout /t 5 /nobreak

REM Check health
echo.
echo Checking service health...

REM Backend health check
echo Checking backend...
curl -s http://localhost:8000/api/health > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend is not responding
    echo Check logs with: docker-compose logs backend
) else (
    echo [OK] Backend is running
)

REM Frontend check
echo Checking frontend...
curl -s http://localhost > nul 2>&1
if errorlevel 1 (
    echo [ERROR] Frontend is not responding
    echo Check logs with: docker-compose logs frontend
) else (
    echo [OK] Frontend is running
)

REM Success message
echo.
echo ============================================================
echo                   Services Started!
echo ============================================================
echo.
echo Frontend:        http://localhost
echo Backend API:     http://localhost:8000
echo API Docs:        http://localhost:8000/docs
echo Health Check:    http://localhost:8000/api/health
echo.
echo Useful commands:
echo   View logs:          docker-compose logs -f
echo   View backend logs:  docker-compose logs -f backend
echo   View frontend logs: docker-compose logs -f frontend
echo   Stop services:      docker-compose down
echo   Rebuild:            docker-compose build --no-cache
echo.
echo Next steps:
echo   1. Open http://localhost in your browser
echo   2. Try example queries or generate leadership update
echo   3. Check backend logs for any errors
echo.
echo [OK] Ready to go!
echo.

pause
