import asyncio
import requests
import time
from telethon import TelegramClient

# =========================================================================
# TELEGRAM USER-BOT KÖPRÜSÜ (@ucretsizderinlikbot'tan Veri Çekme)
# =========================================================================
# UYARI: Telegram API kuralları gereği bir BOT başka bir BOTA mesaj atamaz.
# Bu yüzden bu işlemi Telegram hesabınız üzerinden (bir Kullanıcı olarak) 
# yapmalıyız. Bu script, sizin adınıza hedef bota istek atıp cevabı okur ve 
# Render API'sine (kendi sisteminize) "Matriks" verisiymiş gibi gönderir.
# =========================================================================

# 1. Aşama: my.telegram.org adresine gidip "API Development Tools" 
#    kısmından kendi Telegram hesabınız için bir API_ID ve API_HASH almalısınız.
API_ID = 1234567  # BURAYA KENDİ ID'NİZİ YAZIN
API_HASH = "string_hash_buraya_gelecek" # BURAYA KENDİ HASH'İNİZİ YAZIN
SESSION_NAME = "akd_scraper_session" # Giriş yapıldığında oluşacak dosya adı

# 2. Aşama: Hedef bot ve Sınır ayarları
TARGET_BOT = "ucretsizderinlikbot"
RENDER_API_URL = "https://telegramweb-gd62.onrender.com/api/push-matriks-akd"
API_TOKEN = "MATRIKS_GIZLI_TOKEN_123" # main.py ve .env'deki şifreyle aynı olmalı

# Taramasını istediğiniz ve kendi botunuzda sergilenecek favori borsa hisseleri
SYMBOLS_TO_TRACK = ["THYAO", "EREGL", "TUPRS", "YKBNK", "ISCTR", "ASELS", "BIMAS"]
UPDATE_INTERVAL = 60 # Hedef bota flood (spam) yapmamak için bekleme süresi

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def parse_bot_response(symbol, text):
    """
    Hedef botun (ucretsizderinlikbot) attığı mesajı analiz edip bizim
    profesyonel terminalin anlayacağı JSON kalıbına dönüştürür.
    Not: Hedef botun mesaj formatı değişirse bu regex/split kısmı güncellenmelidir.
    """
    # Örnek Varsayılan Şema (Gelen Metni Parçaladığımızı Varsayıyoruz)
    # Satın almadan bu özelliği kullanacaksanız, hedefin gönderdiği formata
    # göre ufak string split işlemleri eklenmesi gerekir. Şimdilik sistem 
    # uyumluluğunu test etmek için "mock" veri döndürüyor.
    
    return {
        "symbol": symbol,
        "buyers": [
            {"kurum": "Bank of America", "lot": "2,450,000", "maliyet": "---"},
            {"kurum": "Yatirim Finans", "lot": "1,100,000", "maliyet": "---"},
            {"kurum": "Is Yatirim", "lot": "850,000", "maliyet": "---"}
        ],
        "sellers": [
            {"kurum": "Global", "lot": "-1,800,000", "maliyet": "---"},
            {"kurum": "Gedik", "lot": "-900,000", "maliyet": "---"}
        ],
        "source": "UcretsizDerinlikBot (Scraped)",
        "status": "Güncel",
        "net_fark": "---"
    }

async def fetch_and_push(symbol):
    print(f"[{time.strftime('%H:%M:%S')}] {symbol} verisi '{TARGET_BOT}' hedefinden isteniyor...")
    
    try:
        # Bota mesaj gönder (Kullanıcı klavyeden yazıyormuş gibi)
        await client.send_message(TARGET_BOT, f"/akd {symbol}")
        
        # Botun cevabını bekle
        await asyncio.sleep(4) 
        
        # Son mesajları al (0 indeksli olan bota attığımız mesaj, 1 veya 2 indeksli olan botun cevabıdır)
        messages = await client.get_messages(TARGET_BOT, limit=2)
        
        bot_response = ""
        for msg in messages:
            if msg.sender_id != (await client.get_me()).id:
                bot_response = msg.text
                break
                
        if bot_response:
            print(f"✅ Bot cevap verdi ({symbol}). Sisteme yükleniyor...")
            parsed_data = parse_bot_response(symbol, bot_response)
            
            payload = {
                "token": API_TOKEN,
                "data": parsed_data
            }
            # Kendi sunucumuza gönder
            res = requests.post(f"{RENDER_API_URL}/{symbol}", json=payload, timeout=5)
            
            if res.status_code == 200:
                print(f"🚀 {symbol} verisi kendi sisteminize başarıyla işlendi!")
            else:
                print(f"❌ Aktarım hatası: {res.status_code} - {res.text}")
        else:
            print(f"❌ Bottan {symbol} için cevap alınamadı veya gecikti.")
            
    except Exception as e:
        print(f"❌ Ağ hatası: {e}")

async def main():
    print("==================================================")
    print(" 🤖 TELEGRAM USER-BOT KÖPRÜSÜ BAŞLATILIYOR 🤖 ")
    print("==================================================")
    print("İlk girişte sizden telefon numaranız ve Telegram'dan gelen doğrulama kodunuz istenecektir.")
    
    await client.start()
    print("\n✅ Hesaba giriş yapıldı. Dinleme Döngüsü Başlatılıyor...\n")
    
    while True:
        for symbol in SYMBOLS_TO_TRACK:
            await fetch_and_push(symbol)
            # Ban yememek veya flood filtresine takılmamak için araya 3 saniye koyuyoruz.
            await asyncio.sleep(3) 
            
        print(f"\n🔄 Döngü tamamlandı. {UPDATE_INTERVAL} saniye bekleniyor...\n")
        await asyncio.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    # BU SCRİPTİ ÇALIŞTIRMAK İÇİN ŞU KÜTÜPHANELERİ YÜKLEYİN:
    # pip install telethon requests
    client.loop.run_until_complete(main())
