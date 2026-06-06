@echo off
:: Fixes the weird symbols/emojis by forcing UTF-8 encoding
chcp 65001 >nul

echo 📦 Step 1: Checking and installing dependencies...
python -m pip install --upgrade pip
python -m pip install customtkinter pyinstaller

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Failed to install dependencies. Make sure Python is installed and connected to the internet.
    goto end
)

echo.
echo 🚀 Step 2: Compiling app with PyInstaller...
:: Running PyInstaller through 'python -m' bypasses the "not recognized" Windows PATH bug
:: '--collect-all customtkinter' ensures your UI theme and styles aren't left behind
python -m PyInstaller --onefile --noconsole --collect-all customtkinter app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Build failed! Check the error messages above.
    goto end
)

echo.
echo 🎉 Build complete! Check the 'dist' folder for your executable.
:end
echo.
pause