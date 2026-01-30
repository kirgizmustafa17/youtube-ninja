@echo off
chcp 65001 >nul
echo YouTube Ninja Kurulum Baslatiliyor...
echo -----------------------------------

if not exist "venv" (
    echo [1/3] Virtual environment olusturuluyor...
    python -m venv venv
) else (
    echo [1/3] venv zaten mevcut, geciliyor...
)

echo [2/3] Virtual environment aktif ediliyor...
call venv\Scripts\activate.bat

echo [3/3] Bagimliliklar yukleniyor...
pip install -r requirements.txt

echo.
echo -----------------------------------
echo Kurulum Tamamlandi!
echo run_windows.bat dosyasi ile uygulamayi baslatabilirsiniz.
pause
