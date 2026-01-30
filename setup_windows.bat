@echo off
echo YouTube Ninja Kurulum Baslatiliyor...
echo -----------------------------------

if not exist venv (
    echo [1/3] Virtual environment (venv) olusturuluyor...
    python -m venv venv
) else (
    echo [1/3] venv zaten mevcut, geciliyor...
)

echo [2/3] Virtual environment aktif ediliyor...
call venv\Scripts\activate

echo [3/3] Bagimliliklar yukleniyor/guncelleniyor...
pip install -r requirements.txt

echo.
echo -----------------------------------
echo Kurulum Tamamlandi!
echo 'run_windows.bat' dosyasi ile uygulamayi baslatabilirsiniz.
pause
