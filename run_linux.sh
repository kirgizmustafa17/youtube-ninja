#!/bin/bash

if [ ! -d "venv" ]; then
    echo "HATA: Virtual environment bulunamadı!"
    echo "Lütfen önce './setup_linux.sh' dosyasını çalıştırın."
    exit 1
fi

echo "YouTube Ninja Başlatılıyor..."
source venv/bin/activate
python3 main.py
