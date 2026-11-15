@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SmartVitals AI Launcher

echo.
echo ========================================
echo   SmartVitals AI - Launcher
echo ========================================
echo.

set "UV="
for /f "delims=" %%U in ('where uv 2^>nul') do if not defined UV set "UV=%%U"

if not defined UV (
    echo [1/5] uv was not found. Installing uv...
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; try { irm https://astral.sh/uv/install.ps1 | iex } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 goto uv_install_failed

    if exist "%USERPROFILE%\.local\bin\uv.exe" set "UV=%USERPROFILE%\.local\bin\uv.exe"
    if not defined UV (
        for /f "delims=" %%U in ('where uv 2^>nul') do if not defined UV set "UV=%%U"
    )
    if not defined UV goto uv_install_failed
) else (
    echo [1/5] uv is installed.
)

"%UV%" --version
if errorlevel 1 goto uv_install_failed

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo [2/5] Creating the project environment with uv-managed Python...
    "%UV%" venv .venv --python 3.12
    if errorlevel 1 goto setup_failed
) else (
    echo [2/5] Project environment already exists.
)

echo.
echo [3/5] Checking and installing project dependencies...
"%UV%" pip install --python .venv\Scripts\python.exe -r requirements.txt
if errorlevel 1 goto setup_failed

echo.
echo [4/5] Starting the SmartVitals API...
powershell -NoLogo -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 2 -UseBasicParsing; if ($response.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
if not errorlevel 1 (
    echo     An app is already responding at http://127.0.0.1:8000.
) else (
    set "SMARTVITALS_APP=%CD%"
    set "SMARTVITALS_UV=%UV%"
    powershell -NoLogo -NoProfile -Command "$ErrorActionPreference = 'Stop'; try { $root = $env:SMARTVITALS_APP; Start-Process -FilePath $env:SMARTVITALS_UV -ArgumentList @('run','--python','.venv\Scripts\python.exe','-m','uvicorn','backend.main:app','--host','127.0.0.1','--port','8000') -WorkingDirectory $root -RedirectStandardOutput (Join-Path $root 'server-output.log') -RedirectStandardError (Join-Path $root 'server-error.log') -PassThru | Out-Null } catch { Write-Error $_; exit 1 }"
    if errorlevel 1 goto setup_failed
)

echo.
echo [5/5] Waiting for the app to become ready...
set /a WAIT_COUNT=0
:wait_for_app
powershell -NoLogo -NoProfile -Command "try { $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/status' -TimeoutSec 2 -UseBasicParsing; if ($response.StatusCode -eq 200) { exit 0 } } catch {}; exit 1" >nul 2>&1
if not errorlevel 1 goto app_ready
set /a WAIT_COUNT+=1
if %WAIT_COUNT% geq 60 goto app_timeout
echo     Still starting... (%WAIT_COUNT%/60)
powershell -NoLogo -NoProfile -Command "Start-Sleep -Seconds 2"
goto wait_for_app

:app_ready
echo.
echo SmartVitals AI is ready at http://127.0.0.1:8000
echo The server will continue running in the background.
echo Server logs: server-output.log and server-error.log
start "" "http://127.0.0.1:8000"
echo.
pause
exit /b 0

:uv_install_failed
echo.
echo ERROR: uv could not be installed or started.
echo Check your internet connection, then install uv from https://docs.astral.sh/uv/
pause
exit /b 1

:setup_failed
echo.
echo ERROR: Setup failed. Review the error above and try again.
pause
exit /b 1

:app_timeout
echo.
echo ERROR: The app did not become ready within 2 minutes.
echo Check server-output.log and server-error.log for startup errors.
pause
exit /b 1
