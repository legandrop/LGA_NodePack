@echo off
:: Copy the script to temp so it survives git checkout (which may delete repo files)
copy /Y "%~dp0git-safe-merge.ps1" "%TEMP%\git-safe-merge.ps1" >nul
for %%I in ("%~dp0..") do set "REPO_DIR=%%~fI"
powershell -ExecutionPolicy Bypass -File "%TEMP%\git-safe-merge.ps1" -WorkingDir "%REPO_DIR%"
pause
