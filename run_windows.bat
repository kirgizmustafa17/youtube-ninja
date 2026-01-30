@echo off
chcp 65001 >nul
if not exist "venv" (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once setup_windows.bat dosyasini calistirin.
    pause
    exit /b
)

echo YouTube Ninja Baslatiliyor...
call venv\Scripts\activate.bat
python main.py
