#!/bin/bash

echo "YouTube Ninja Kurulum Başlatılıyor..."
echo "-----------------------------------"

if [ ! -d "venv" ]; then
    echo "[1/3] Virtual environment (venv) oluşturuluyor..."
    python3 -m venv venv
else
    echo "[1/3] venv zaten mevcut, geçiliyor..."
fi

echo "[2/3] Virtual environment aktif ediliyor..."
source venv/bin/activate

echo "[3/3] Bağımlılıklar yükleniyor/güncelleniyor..."
pip install -r requirements.txt

echo ""
echo "-----------------------------------"
echo "Kurulum Tamamlandı!"
echo "'./run_linux.sh' dosyası ile uygulamayı başlatabilirsiniz."
echo "Eğer izin hatası alırsanız: chmod +x run_linux.sh"
