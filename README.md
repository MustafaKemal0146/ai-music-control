# AI Müzik Kontrolü

Bilgisayar görüşü ve yapay zeka kullanarak kafa hareketleriyle sistem genelinde medya kontrolü sağlayan bir Python uygulaması.

## Özellikler

- Gerçek zamanlı yüz algılama ve yüz işaretleri takibi
- Kafa hareketleriyle medya kontrolü:
  - Kafayı sağa çevirme: Sonraki şarkı
  - Kafayı sola çevirme: Önceki şarkı
  - Kafayı yukarı/aşağı hareket ettirme: Oynat/Duraklat
  - Özel hareket algılama: Sessiz/Sesli geçiş
- Kullanıcı dostu arayüz, video akışı ve günlük konsolu
- Spotify, YouTube, Apple Music gibi herhangi bir medya uygulamasını kontrol edebilme

## Gereksinimler

- Python 3.7+
- Webcam
- requirements.txt dosyasında listelenen bağımlılıklar

## Kurulum

1. Bu depoyu klonlayın
2. Bağımlılıkları yükleyin:
   ```
   pip install -r requirements.txt
   ```

## Kullanım

1. Önce kontrol etmek istediğiniz medya uygulamasını açın (Spotify, YouTube, vb.)
2. Ardından uygulamayı çalıştırın:
   ```
   python main.py
   ```
3. Kafa hareketlerinizle medya kontrolünü sağlayın

## Proje Yapısı

- `main.py`: Uygulama giriş noktası
- `face_detector.py`: Yüz algılama ve işaret takibi modülü
- `music_controller.py`: Medya kontrolü modülü (sistem genelinde medya tuşlarını simüle eder)
- `gui.py`: PyQt5 tabanlı grafik kullanıcı arayüzü
- `utils.py`: Yardımcı fonksiyonlar

## Lisans

Detaylar için LICENSE dosyasına bakın. 

