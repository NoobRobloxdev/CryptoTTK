@echo off
title CryptoTTK Ultimate Suite
cls
:menu
echo ===================================
echo     CryptoTTK Ultimate Suite
echo ===================================
echo 1. Nainstalovat potrebne kniznice (pip install)
echo 2. Spustit Crypter (Sifrovanie)
echo 3. Spustit Uncrypter (Desifrovanie)
echo 4. Spustit OBIDVOJE naraz
echo 5. Koniec
echo ===================================
set /p opt="Vyber moznost (1-5): "

if "%opt%"=="1" (
    echo.
    echo Instalujem kniznice...
    pip install cryptography pillow qrcode pyzbar
    pause
    goto menu
)
if "%opt%"=="2" start python crypter.py & goto menu
if "%opt%"=="3" start python uncrypter.py & goto menu
if "%opt%"=="4" (
    start python crypter.py
    start python uncrypter.py
    goto menu
)
if "%opt%"=="5" exit
goto menu