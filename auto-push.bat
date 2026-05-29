@echo off
echo.
echo ========================================
echo   AUTO GIT PUSH
echo ========================================
echo.

REM Get current date and time
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set date_str=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%
set time_str=%datetime:~8,2%:%datetime:~10,2%

echo [1/3] Adding all changes...
git add .

echo [2/3] Committing with timestamp...
git commit -m "Update %date_str% %time_str%"

echo [3/3] Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo   DONE! Pushed at %time_str%
echo ========================================
echo.
timeout /t 3
