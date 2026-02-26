import asyncio
import os
import time
import requests
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto

API_ID = 37031232
API_HASH = "518b15f17950300182c1edf6921e7c92"
SESSION_NAME = "akd_scraper_session"

TARGET_BOT = "ucretsizderinlikbot"

# Resimlerin ve verilerin kaydedileceği klasör
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/matriks")
os.makedirs(DATA_DIR, exist_ok=True)

# Takip edilecek hisseler
SYMBOLS_TO_TRACK = ["THYAO", "EREGL", "TUPRS", "YKBNK", "ISCTR", "ASELS", "BIMAS", "SASA", "KCHOL", "SAHOL"]

# Zaman periyotları (hedef botun inline keyboard'undaki butonlar)
TIME_PERIODS = {
    "gunluk": "Günlük",
    "5dk":    "5dk",
    "15dk":   "15dk",
    "30dk":   "30dk",
    "1sa":    "1sa",
    "dunku":  "Dünkü",
    "3g":     "3G",
    "7g":     "7G",
    "14g":    "14G",
    "1ay":    "1Ay",
    "3ay":    "3Ay",
    "6ay":    "6Ay",
    "1yil":   "1Yıl",
    "ay_basi":"Ay Başı",
    "yil_basi":"Yıl Başı"
}

UPDATE_INTERVAL = 90  # saniye - flood koruması

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def get_me_id():
    me = await client.get_me()
    return me.id


async def fetch_akd_image(symbol: str, period_label: str = "Günlük", period_key: str = "gunluk") -> bool:
    """
    Hedef botanrn /akd komutuna cevap olarak gelen fotoğrafı indirir.
    Fotoğrafı data/matriks/{SYMBOL}_akd_{period_key}.jpg olarak kaydeder.
    """
    me_id = await get_me_id()
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} AKD ({period_label}) çekiliyor...")

    try:
        # Komutu gönder
        await client.send_message(TARGET_BOT, f"/akd {symbol}")
        await asyncio.sleep(5)

        # Son mesajları al
        messages = await client.get_messages(TARGET_BOT, limit=4)

        bot_msg = None
        for msg in messages:
            if msg.sender_id != me_id:
                bot_msg = msg
                break

        if not bot_msg:
            print(f"  ❌ {symbol} AKD: Bot cevap vermedi")
            return False

        # Eğer bot fotoğraf gönderdiyse kaydet
        if bot_msg.media and isinstance(bot_msg.media, MessageMediaPhoto):
            save_path = os.path.join(DATA_DIR, f"{symbol}_akd_gunluk.jpg")
            await bot_msg.download_media(file=save_path)
            print(f"  ✅ {symbol} AKD fotoğrafı kaydedildi: {save_path}")

            # Inline keyboard'a tıklayarak diğer periyotları da çek (sadece ana döngüde günlük)
            return True

        # Eğer metin cevap geldiyse kaydet
        elif bot_msg.text:
            text_path = os.path.join(DATA_DIR, f"{symbol}_akd_gunluk.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(bot_msg.text)
            print(f"  ✅ {symbol} AKD metin kaydedildi")
            return True

        print(f"  ⚠️ {symbol} AKD: Tanımsız cevap tipi")
        return False

    except Exception as e:
        print(f"  ❌ {symbol} AKD hata: {e}")
        return False


async def fetch_akd_period(symbol: str, period_key: str):
    """
    Belirli bir periyot için AKD fotoğrafını çeker.
    Önce günlük komutu gönderir, ardından inline button'a tıklar.
    """
    me_id = await get_me_id()
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} AKD ({period_key}) çekiliyor...")

    try:
        # Komutu gönder
        await client.send_message(TARGET_BOT, f"/akd {symbol}")
        await asyncio.sleep(5)

        # Son bot mesajını bul
        messages = await client.get_messages(TARGET_BOT, limit=4)
        bot_msg = None
        for msg in messages:
            if msg.sender_id != me_id:
                bot_msg = msg
                break

        if not bot_msg:
            return False

        # Inline keyboard'da periyot butonuna tıkla
        if bot_msg.buttons:
            period_label = TIME_PERIODS.get(period_key, period_key)
            for row in bot_msg.buttons:
                for btn in row:
                    if btn.text.strip() == period_label:
                        await btn.click()
                        await asyncio.sleep(4)
                        # Tıklama sonrası güncellenmiş mesajı al
                        updated = await client.get_messages(TARGET_BOT, limit=2)
                        for msg in updated:
                            if msg.sender_id != me_id and msg.media:
                                save_path = os.path.join(DATA_DIR, f"{symbol}_akd_{period_key}.jpg")
                                await msg.download_media(file=save_path)
                                print(f"  ✅ {symbol} AKD {period_key} kaydedildi")
                                return True

        return False
    except Exception as e:
        print(f"  ❌ {symbol} AKD {period_key} hata: {e}")
        return False


async def fetch_derinlik_image(symbol: str) -> bool:
    """
    /derinlik komutuna gelen fotoğrafı (25 kademe order book) indirir
    ve data/matriks/{SYMBOL}_derinlik.jpg olarak kaydeder.
    """
    me_id = await get_me_id()
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} Derinlik (25K) çekiliyor...")

    try:
        await client.send_message(TARGET_BOT, f"/derinlik {symbol}")
        await asyncio.sleep(6)

        messages = await client.get_messages(TARGET_BOT, limit=4)
        for msg in messages:
            if msg.sender_id != me_id:
                if msg.media and isinstance(msg.media, MessageMediaPhoto):
                    save_path = os.path.join(DATA_DIR, f"{symbol}_derinlik.jpg")
                    await msg.download_media(file=save_path)
                    print(f"  ✅ {symbol} Derinlik fotoğrafı kaydedildi")
                    return True
                elif msg.text:
                    text_path = os.path.join(DATA_DIR, f"{symbol}_derinlik.txt")
                    with open(text_path, "w", encoding="utf-8") as f:
                        f.write(msg.text)
                    print(f"  ✅ {symbol} Derinlik metin kaydedildi")
                    return True

        print(f"  ❌ {symbol} Derinlik: Cevap yok")
        return False

    except Exception as e:
        print(f"  ❌ {symbol} Derinlik hata: {e}")
        return False


async def main():
    print("=" * 54)
    print("  VERI KOPRUSU v2 — AKD FOTOGRAF + DERINLIK 25K")
    print("=" * 54)

    await client.start()
    me = await client.get_me()
    print(f"Giriş: {me.first_name} ({me.id})\n")

    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'='*54}")
        print(f"  DONGU #{cycle}  —  {time.strftime('%H:%M:%S')}")
        print(f"{'='*54}")

        for symbol in SYMBOLS_TO_TRACK:
            # AKD günlük fotoğrafı çek
            await fetch_akd_image(symbol)
            await asyncio.sleep(4)

            # Derinlik (25 kademe order book) fotoğrafı çek
            await fetch_derinlik_image(symbol)
            await asyncio.sleep(6)

        print(f"\n✓ Döngü #{cycle} tamamlandı. {UPDATE_INTERVAL}s bekleniyor...\n")
        await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nKapatılıyor...")
    finally:
        loop.run_until_complete(client.disconnect())
        loop.close()
