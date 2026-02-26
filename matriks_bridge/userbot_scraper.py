import asyncio
import re
import requests
import time
from telethon import TelegramClient

API_ID = 37031232
API_HASH = "518b15f17950300182c1edf6921e7c92"
SESSION_NAME = "akd_scraper_session"

TARGET_BOT = "ucretsizderinlikbot"
RENDER_API_URL = "https://telegramweb-gd62.onrender.com/api/push-matriks"
API_TOKEN = "MATRIKS_GIZLI_TOKEN_123"

SYMBOLS_TO_TRACK = ["THYAO", "EREGL", "TUPRS", "YKBNK", "ISCTR", "ASELS", "BIMAS"]
UPDATE_INTERVAL = 60

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

# -----------------------------------------------------------------------
# PARSE: Hedef botun /akd cevabını parçala
# -----------------------------------------------------------------------
def parse_akd_response(symbol, text):
    """
    ucretsizderinlikbot'un /akd cevabını parçalayıp standart JSON'a çevirir.
    Satır satır gezerek ALAN ve SATAN tablolarını ayırt eder.
    """
    buyers = []
    sellers = []
    
    if not text:
        return None

    lines = text.strip().split('\n')
    mode = None

    for line in lines:
        line = line.strip()
        # Alış/satış section başlıklarını yakala
        if re.search(r'alan|alış|net alım', line, re.IGNORECASE):
            mode = 'buy'
            continue
        elif re.search(r'satan|satış|net satım', line, re.IGNORECASE):
            mode = 'sell'
            continue

        # Satır içinde kurum ve lot bilgisi var mı?
        # Örnek format: "İş Yatırım    2.450.000" veya "İŞ YAT  |  2,450,000"
        match = re.search(r'([A-ZÇĞİÖŞÜa-zçğışöşü\s\.]+?)\s+[\|]?\s*([\d\.,]+)', line)
        if match and mode:
            kurum = match.group(1).strip()
            lot = match.group(2).strip()
            if len(kurum) > 2 and any(c.isdigit() for c in lot):
                entry = {"kurum": kurum[:22], "lot": lot, "maliyet": "---"}
                if mode == 'buy':
                    buyers.append(entry)
                else:
                    sellers.append(entry)

    # Eğer hiç parse edemediyse metin bazlı ham cevabı gönder
    if not buyers and not sellers:
        return {
            "symbol": symbol,
            "raw": text,
            "buyers": [],
            "sellers": [],
            "status": "parse_edilemedi"
        }

    return {
        "symbol": symbol,
        "buyers": buyers[:10],
        "sellers": sellers[:10],
        "status": "guncel"
    }

# -----------------------------------------------------------------------
# PARSE: Hedef botun /derinlik cevabını parçala (Emir Defteri / Order Book)
# -----------------------------------------------------------------------
def parse_derinlik_response(symbol, text):
    """
    ucretsizderinlikbot'un /derinlik cevabını parçalayıp
    alış ve satış tarafındaki fiyat/lot seviyelerine böler.
    Beklenen format örnekleri:
      311.45   150,000     veya     150,000   311.45
    """
    if not text:
        return None

    bids = []   # Alış tarafı
    asks = []   # Satış tarafı

    lines = text.strip().split('\n')
    mode = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        lower = line.lower()
        if re.search(r'alış|bid|al[^t]', lower):
            mode = 'bid'
            continue
        elif re.search(r'satış|ask|sat', lower):
            mode = 'ask'
            continue

        # Sayı çiftini yakala: fiyat ve miktar
        nums = re.findall(r'[\d]{2,}[\.,][\d]+', line)
        if len(nums) >= 2 and mode:
            try:
                # İlk rakam fiyat, ikinci miktar — ya da ters
                a = float(nums[0].replace('.', '').replace(',', '.'))
                b = float(nums[1].replace('.', '').replace(',', '.'))
                # Genellikle fiyat daha küçük sayıdır (örn: 311.45 vs 150000)
                if a < b:
                    price, qty = nums[0], nums[1]
                else:
                    price, qty = nums[1], nums[0]

                entry = {"fiyat": price, "adet": qty}
                if mode == 'bid':
                    bids.append(entry)
                elif mode == 'ask':
                    asks.append(entry)
            except:
                continue

    if not bids and not asks:
        return {
            "symbol": symbol,
            "raw": text,
            "bids": [],
            "asks": [],
            "status": "parse_edilemedi"
        }

    return {
        "symbol": symbol,
        "bids": bids[:10],
        "asks": asks[:10],
        "status": "guncel"
    }

# -----------------------------------------------------------------------
# ANA DÖNGÜ: Hem AKD hem Derinlik verisini çek ve Render'a gönder
# -----------------------------------------------------------------------
async def fetch_and_push(symbol):
    me = await client.get_me()

    # 1) AKD verisini çek
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} AKD -> '{TARGET_BOT}'")
    await client.send_message(TARGET_BOT, f"/akd {symbol}")
    await asyncio.sleep(4)
    messages = await client.get_messages(TARGET_BOT, limit=3)
    akd_text = ""
    for msg in messages:
        if msg.sender_id != me.id and msg.text:
            akd_text = msg.text
            break

    if akd_text:
        akd_data = parse_akd_response(symbol, akd_text)
        if akd_data:
            res = requests.post(
                f"{RENDER_API_URL}-akd/{symbol}",
                json={"token": API_TOKEN, "data": akd_data},
                timeout=6
            )
            status = "OK" if res.status_code == 200 else f"HATA {res.status_code}"
            print(f"  AKD -> {status}")
    else:
        print(f"  AKD -> Cevap yok")

    await asyncio.sleep(3)

    # 2) Derinlik (Order Book) verisini çek
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} DErinlik -> '{TARGET_BOT}'")
    await client.send_message(TARGET_BOT, f"/derinlik {symbol}")
    await asyncio.sleep(5)
    messages = await client.get_messages(TARGET_BOT, limit=3)
    derinlik_text = ""
    for msg in messages:
        if msg.sender_id != me.id and msg.text:
            derinlik_text = msg.text
            break

    if derinlik_text:
        derinlik_data = parse_derinlik_response(symbol, derinlik_text)
        if derinlik_data:
            res = requests.post(
                f"{RENDER_API_URL}-derinlik/{symbol}",
                json={"token": API_TOKEN, "data": derinlik_data},
                timeout=6
            )
            status = "OK" if res.status_code == 200 else f"HATA {res.status_code}"
            print(f"  Derinlik -> {status}")
    else:
        print(f"  Derinlik -> Cevap yok")

    # Her hisseden sonra kısa bekleme (flood koruması)
    await asyncio.sleep(5)


async def main():
    print("=" * 52)
    print("  VERI KOPRUSU BASLATILIYOR")
    print("  AKD + DEriNLiK (order book)")
    print("=" * 52)

    await client.start()
    print("Hesaba giris yapildi. Dongu basliyor...\n")

    while True:
        for symbol in SYMBOLS_TO_TRACK:
            try:
                await fetch_and_push(symbol)
            except Exception as e:
                print(f"  HATA ({symbol}): {e}")

        print(f"\nDongu tamamlandi. {UPDATE_INTERVAL}s bekleniyor...\n")
        await asyncio.sleep(UPDATE_INTERVAL)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nKapatiliyor.")
    finally:
        loop.run_until_complete(client.disconnect())
        loop.close()
