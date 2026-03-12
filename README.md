# PARİBU MENKUL DEĞER — Profesyonel Veri Terminali

Bu proje, Borsa İstanbul (BIST) verilerini anlık olarak takip eden, teknik analiz ve aracı kurum dağılımı (AKD) raporları sunan profesyonel bir veri terminali botudur.

## ▣ Öne Çıkan Özellikler

### ◉ Veri Terminali
- **Hisse Radar:** Günün hacim patlaması yapan ve trende giren hisselerini otomatik analiz eder.
- **Teknik Tarama:** RSI, MACD ve Hareketli Ortalamalar (EMA/SMA) bazlı anlık teknik analiz sunar.
- **AKD Tarama:** Hangi kurumun hangi hissede alıcı veya satıcı olduğunu gösteren anlık aracı kurum dağılımı.
- **Takas Tarama:** MKK verileriyle ana saklamacı kurumların pay değişimlerini takip eder.
- **KAP Ajan:** Borsaya düşen KAP bildirimlerini saniyeler içinde analiz ederek kullanıcıya ulaştırır.

### ■ Matriks Canlı Terminal (Entegre)
- **25 Kademe Derinlik:** MatriksIQ üzerinden canlı derinlik tablosu yakalama.
- **Aracı Kurum Dağılımı:** F3 kısayolu ile anlık canlı AKD görüntüsü.
- **Zaman ve Satış:** Canlı işlem akışı.
- **Teorik Eşleşme:** Açılış ve kapanış seanslarında teorik fiyat hesaplaması.
- **Teknik Grafik:** Canlı ve gelişmiş teknik grafik ekran görüntüleri.

## ◈ Kurulum ve Başlatma

1. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

2. `.env` yapılandırmasını yapın:
   - `TELEGRAM_BOT_TOKEN`: @BotFather'dan alınan API anahtarı.

3. Sistemi başlatın:
   ```bash
   python src/main.py
   ```

## ▣ Komut Seti

| Komut | Açıklama |
|-------|----------|
| `/radar` | BIST Günlük Fırsatlar ve Hacim Analizi |
| `/teknik` | Hızlı indikatör taraması (Örn: `/teknik THYAO`) |
| `/akdtara` | Kurum Alım/Satım odaklı AKD taraması |
| `/takastara` | Takas ve Saklama verileri analizi |
| `/kap` | Son dakika KAP bildirimleri |
| `/derinlik` | [Matriks] 25 Kademe Derinlik Tablosu |
| `/grafik` | [Matriks] Canlı Teknik Grafik |

---
_© 2026 PARİBU MENKUL DEĞER. Tüm hakları saklıdır._
