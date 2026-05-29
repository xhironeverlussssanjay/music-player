@echo off
cd ..
echo.
echo ========================================
echo   GIT PUSH AUTOMATION
echo ========================================
echo.

REM Cek status
echo [1/4] Checking status...
git status

echo.
echo [2/4] Adding all changes...
git add .

echo.
set /p commit_msg="[3/4] Enter commit message: "
git commit -m "%commit_msg%"

echo.
echo [4/4] Pushing to GitHub...
git push origin master

echo.
echo ========================================
echo   DONE! Check GitHub repository
echo ========================================
echo.
pause
