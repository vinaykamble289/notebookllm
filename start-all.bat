@echo off
echo ========================================
echo RAG AI Assistant - Quick Start
echo ========================================
echo.

REM Start backend in new window
echo Starting Backend Server...
start "RAG Backend" cmd /k "cd backend && start.bat"

REM Wait a bit for backend to start
timeout /t 5 /nobreak

REM Start frontend in new window
echo Starting Frontend...
start "RAG Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window
echo (Servers will continue running)
echo ========================================
pause
