import time
import requests
import json
import os
import win32com.client  # pip install pywin32
import pywintypes
import threading

# --- AYARLAR ---
API_URL = "https://telegramweb-gd62.onrender.com/api/push-matriks-akd"
API_TOKEN = "MATRIKS_GIZLI_TOKEN_123" # Bot sunucusundaki .env MATRIKS_BRIDGE_TOKEN ile aynı olmalı
UPDATE_INTERVAL_SEC = 2.0  # Kaç saniyede bir veriyi okuyup Render'a atsın?

# DDE İLE TAKİP EDİLECEK HİSSELER (Bunu zamanla dışarıdan txt'den okutabiliriz, şimdilik sabit)
SYMBOLS_TO_TRACK = ["THYAO", "EREGL", "TUPRS", "YKBNK", "ISCTR", "ASELS", "BIMAS"]

print("==================================================")
print(" ⚡ MATRİKS -> RENDER (PRO OTONOM DDE KÖPRÜSÜ) ⚡ ")
print("==================================================")
print("Bu program Matriks terminalinin arka plan DDE (Canlı Aktarım)")
print("özelliğini kullanarak, PENCERELERİ AÇMANIZA BİLE GEREK KALMADAN")
print("belirlediğiniz hisselerin AKD/Derinlik verilerini sessizce okur")
print("ve saniyede bir Telegram sunucusuna postalar.\n")
print(f"Takip Edilen Hisseler: {', '.join(SYMBOLS_TO_TRACK)}")
print("==================================================\n")

def get_dde_data():
    """
    Python üzerinden bir DDE İstemcisi kanalı açar.
    Not: Bu kısım Matriks'in MTX dde sunucusu çalıştığı sürece (Matriks açıkken)
    Excel olmadan doğrudan ram'den veriyi okumanızı sağlar.
    """
    try:
        # Gerçek bir DDE bağlantısı ddeml veya win32ui üzerinden kurulur
        # Basit implementasyon için DDE Client sınıfı oluşturulur
        import win32ui
        import dde
        
        server = dde.CreateServer()
        server.Create("MatriksListener")
        
        conversation = dde.CreateConversation(server)
        
        # MTX = Matriks DDE Sunucusu Adı, QUOTE = Genel Veri Penceresi
        conversation.ConnectTo("MTX", "QUOTE")
        return conversation
    except Exception as e:
        print(f"DDE Bağlantı Hatası (Matriks açık mı?): {e}")
        return None

def fetch_akd_via_dde(conversation, symbol):
    """
    Belirli bir DDE formatında kurumu ve lotunu okur.
    (Matriks DDE formatında genelde ALICI1, SATICI1 vs şeklinde linkler olur)
    Şimdilik sistemin nasıl kurulacağını göstermek için taslak yapıdır.
    Satın alımdan sonra Matriks'ten "Excel'e Aktar" ile gerçek hücre kodlarını (örn: =MTX|QUOTE!THYAO.ALICI1_K) tespit edip buraya yazacağız.
    """
    if not conversation:
        return None
    
    try:
        # Örnek Matriks DDE komutu: symbol + ".ALAKD1" tarzı
        # Bu kodları Matriks Excel'deki formüle göre tam şekillendireceğiz (Satın alım bitince)
        
        # Simüle Edilmiş bir yapı (Gerçek hücre kodlarını senin Matriksinden alacağız)
        buyers = [
            {"kurum": "Bank of America", "lot": "1,500,000", "maliyet": "301.20"},
            {"kurum": "Yapi Kredi", "lot": "850,000", "maliyet": "302.10"},
            {"kurum": "Is Yatirim", "lot": "450,000", "maliyet": "301.50"}
        ]
        
        sellers = [
            {"kurum": "Info Yatirim", "lot": "-900,000", "maliyet": "299.10"},
            {"kurum": "Gedik", "lot": "-600,000", "maliyet": "299.80"}
        ]

        return {
            "symbol": symbol,
            "buyers": buyers,
            "sellers": sellers,
            "source": "Matriks Terminal PRO (DDE)",
            "status": "Canlı Eşzamanlı",
            "net_fark": "1,300,000"
        }
    except Exception as e:
        # print(f"Okuma hatası ({symbol}): {e}")
        return None

def worker_thread():
    # Matriks DDE'sine bağlan
    conversation = get_dde_data()
    
    if not conversation:
        print("UYARI: DDE'ye bağlanılamadı. Matriks terminali arkada açık mı emin olun.")
        print("Sistem yine de her 5 saniyede bir bağlanmayı deneyecek...\n")
    
    while True:
        try:
            # Bağlantı düştüyse / ilk başta kurulamadıysa tekrar dene
            if not conversation or not conversation.Connected():
                conversation = get_dde_data()
                
            if conversation:
                for symbol in SYMBOLS_TO_TRACK:
                    akd_data = fetch_akd_via_dde(conversation, symbol)
                    
                    if akd_data:
                        payload = {
                            "token": API_TOKEN,
                            "data": akd_data
                        }
                        
                        try:
                            # Sunucuya gönder (API_URL)
                            res = requests.post(f"{API_URL}/{symbol}", json=payload, timeout=2)
                            if res.status_code == 200:
                                print(f"[{time.strftime('%H:%M:%S')}] ✅ {symbol} verisi güncellendi (OK)")
                            else:
                                print(f"[{time.strftime('%H:%M:%S')}] ❌ Hata: {res.status_code} - {res.text}")
                        except requests.exceptions.RequestException as re:
                            print(f"[{time.strftime('%H:%M:%S')}] ❌ Sunucuya erişilemiyor: {re}")
                            
        except Exception as e:
            print(f"Beklenmeyen döngü hatası: {e}")
            
        time.sleep(UPDATE_INTERVAL_SEC) # 2 saniyede bir turu tekrarla

if __name__ == "__main__":
    t = threading.Thread(target=worker_thread, daemon=True)
    t.start()
    
    # Programın kapanmaması için
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("PROGRAM KAPATILIYOR...")
