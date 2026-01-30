@echo off
if not exist venv (
    echo HATA: Virtual environment bulunamadi!
    echo Lutfen once 'setup_windows.bat' dosyasini calistirin.
    pause
    exit /b
)

echo YouTube Ninja Baslatiliyor...
call venv\Scripts\activate
python main.py
