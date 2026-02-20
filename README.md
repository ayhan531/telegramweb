# Ücretsiz Derinlik Botu (Clone)

Bu proje, `@ucretsizderinlikbot` Telegram botunun temel özelliklerini (derinlik özeti ve grafik) taklit eden bir Python uygulamasıdır.

## Özellikler
- **Hisse Derinlik Özeti:** Anlık fiyat, günlük değişim, hacim ve gün içi en düşük/en yüksek değerler.
- **Teknik Grafikler:** Son 1 aya ait fiyat hareketlerini gösteren görsel grafikler.
- **BIST Desteği:** Borsa İstanbul hisseleri için otomatik `.IS` son eki desteği.

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. `.env` dosyasını düzenleyin:
   - `TELEGRAM_BOT_TOKEN` kısmına @BotFather'dan aldığınız token'ı yapıştırın.

3. Botu çalıştırın:
   ```bash
   python src/main.py
   ```

## Komutlar
- `/start` - Botu başlatır ve hoş geldin mesajı gönderir.
- `/derinlik HISSE` - Belirtilen hissenin derinlik özetini getirir. (Örn: `/derinlik THYAO`)
- `/grafik HISSE` - Belirtilen hissenin 1 aylık grafiğini gönderir.
- `/yardim` - Kullanım kılavuzunu gösterir.

## Not
Ücretsiz veri kaynakları (yfinance) kullanıldığı için veriler yaklaşık 15 dakika gecikmeli olabilir.
