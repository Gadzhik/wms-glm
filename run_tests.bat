@echo off
REM VMS Backend Test Runner for Windows
REM Runs all tests with coverage reporting

echo ==========================================
echo VMS Backend Test Suite
echo ==========================================
echo.

REM Change to backend directory
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -q pytest pytest-asyncio pytest-cov httpx

REM Run tests
echo.
echo Running tests...
echo.

REM Run with coverage
pytest --verbose --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml tests/

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All tests passed!
    echo.
    echo Coverage report generated in: backend\htmlcov\index.html
) else (
    echo.
    echo [ERROR] Some tests failed!
    exit /b 1
)

REM Deactivate virtual environment
deactivate

echo.
echo ==========================================
echo Test run complete
echo ==========================================
pause
