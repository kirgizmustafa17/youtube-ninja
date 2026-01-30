# YouTube Ninja 🎬

Clipboard'dan YouTube linklerini otomatik algılayıp indiren Windows uygulaması.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)

## ✨ Özellikler

- 📋 **Clipboard İzleme** - YouTube linklerini otomatik algılar
- 🎥 **Video İndirme** - 360p'den 8K'ya kadar kalite seçeneği
- 🎵 **MP3 İndirme** - En yüksek kalitede ses
- 📂 **Özel Klasörler** - Video ve müzik için ayrı klasörler
- 🔄 **İndirme Kuyruğu** - Birden fazla video sıraya al
- 📜 **İndirme Geçmişi** - Daha önce indirilenleri takip et
- 🔔 **Bildirim Sesleri** - İndirme tamamlandığında ses
- ⚡ **Otomatik Yeniden Deneme** - Bağlantı kesilirse 3 deneme
- 🔧 **Otomatik Güncelleme** - yt-dlp ve bağımlılıklarını açılışta günceller
- 🦕 **Deno Desteği** - Gelişmiş imza çözümü için Deno runtime entegrasyonu
- 🌍 **Çoklu Dil** - Türkçe ve İngilizce desteği

## 📦 Kurulum

```bash
# Repo'yu klonla
git clone https://github.com/kirgizmustafa17/youtube-ninja.git
cd youtube-ninja

# Virtual environment oluştur
python -m venv venv
.\venv\Scripts\Activate.ps1

# Bağımlılıkları yükle
pip install -r requirements.txt

# Uygulamayı başlat
python main.py
```

## 🚀 Kullanım

1. `python main.py` ile uygulamayı başlat
2. System tray'de YouTube ikonu belirir
3. Herhangi bir YouTube linkini kopyala
4. Otomatik olarak indirme penceresi açılır!

### Tray Menüsü

| Seçenek | Açıklama |
|---------|----------|
| ☑️ MP3 İndir | Ses dosyası indir |
| ☑️ Video İndir | Video dosyası indir |
| 📺 Video Kalitesi | 360p - 8K arası seç |
| 📂 Çıktı Klasörleri | İndirme konumunu değiştir |
| 🌍 Dil | Türkçe / İngilizce seçimi |
| ℹ️ Hakkında | Sürüm bilgisi ve bağış |

## 📁 Dosya Yapısı

```
youtube-ninja/
├── main.py           # Ana uygulama
├── downloader.py     # yt-dlp wrapper
├── config_manager.py # Ayar yönetimi
├── logger.py         # Loglama
├── history.py        # İndirme geçmişi
├── queue_manager.py  # İndirme kuyruğu
├── updater.py        # Otomatik güncelleme
└── ui/
    ├── download_window.py  # İndirme penceresi
    └── styles.py           # UI stilleri
```

## ⚙️ Ayarlar

Ayarlar `config.json` dosyasında saklanır:

```json
{
  "download_mp3": true,
  "download_video": true,
  "video_quality": "1080",
  "output_video_dir": "C:/Users/You/Videos",
  "output_audio_dir": "C:/Users/You/Music"
}
```

## 🎬 Desteklenen Formatlar

### Video Codec Önceliği
- **1440p+**: AV1 → VP9 → HEVC → AVC
- **1080p-**: AVC → VP9 → AV1

### Desteklenen URL'ler
- `youtube.com/watch?v=...`
- `youtu.be/...`
- `youtube.com/shorts/...`
- `music.youtube.com/watch?v=...`

## 📝 Loglar

Loglar `logs/` klasöründe günlük olarak saklanır:
```
logs/app_20260108.log
```

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

## ☕ Bağış

Bu projeyi beğendiyseniz:
[Buy Me a Coffee](https://buymeacoffee.com/)

## 📄 Lisans

MIT License
