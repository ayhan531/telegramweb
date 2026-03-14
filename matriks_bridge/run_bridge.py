import time
import requests
import json
import pyperclip
import re

# --- AYARLAR ---
# Bot sunucusu yerelde çalıştığı için localhost kullanıyoruz
API_URL_AKD = "http://localhost:3000/api/push-matriks-akd"
API_URL_DEPTH = "http://localhost:3000/api/push-matriks-derinlik"
API_TOKEN = "MATRIKS_GIZLI_TOKEN_123" 

print("========================================")
print(" ⚡ MATRİKS TERMINAL -> BOT KÖPRÜSÜ v2 ⚡ ")
print("========================================")
print("1. Matriks'te AKD veya Derinlik tablosunu açın.")
print("2. Ctrl+C ile kopyalayın.")
print("3. Bu program otomatik algılayıp bota gönderecektir.\n")

last_clipboard = ""

def parse_akd(text):
    lines = text.strip().split('\n')
    buyers = []
    sellers = []
    
    # Matriks AKD kopyalama formatını işle (Kurum	Lot	Maliyet	Yüzde)
    for line in lines:
        cols = line.split('\t')
        if len(cols) >= 3:
            kurum = cols[0].strip()
            lot = cols[1].replace('.', '').replace(',', '.')
            try:
                if float(lot) > 0:
                    buyers.append({"kurum": kurum, "lot": lot, "maliyet": cols[2] if len(cols)>2 else "---", "pay": 0})
                elif float(lot) < 0:
                    sellers.append({"kurum": kurum, "lot": str(abs(float(lot))), "maliyet": cols[2] if len(cols)>2 else "---", "pay": 0})
            except: continue
    
    return {
        "buyers": buyers[:10],
        "sellers": sellers[:10],
        "source": "Matriks Terminal (Canlı)",
        "status": "Gerçek Veri"
    }

def parse_derinlik(text):
    lines = text.strip().split('\n')
    bids = []
    asks = []
    
    # Matriks Derinlik formatı: Genelde Alış Fiyat | Alış Lot | Satış Lot | Satış Fiyat
    for line in lines:
        cols = line.split('\t')
        if len(cols) >= 4:
            try:
                bids.append({"price": cols[0], "volume": cols[1]})
                asks.append({"price": cols[3], "volume": cols[2]})
            except: continue
            
    return {
        "bids": bids,
        "asks": asks,
        "source": "Matriks Terminal (Level-2)"
    }

while True:
    try:
        current_clipboard = pyperclip.paste()
        
        if current_clipboard != last_clipboard and len(current_clipboard) > 10:
            last_clipboard = current_clipboard
            
            print("\n🔔 Yeni veri algılandı!")
            symbol = input("Hangi hisse? (Örn: THYAO): ").strip().upper()
            
            if not symbol: continue

            # Basit format kontrolü
            if "\t" in current_clipboard:
                # AKD mi Derinlik mi anlamaya çalışalım
                if any(x in current_clipboard for x in ["Maliyet", "Lot", "Net"]):
                    # AKD
                    data = parse_akd(current_clipboard)
                    print(f"🚀 {symbol} AKD verisi gönderiliyor...")
                    res = requests.post(f"{API_URL_AKD}/{symbol}", json={"token": API_TOKEN, "data": data})
                else:
                    # Derinlik farz et
                    data = parse_derinlik(current_clipboard)
                    print(f"🚀 {symbol} Derinlik verisi gönderiliyor...")
                    res = requests.post(f"{API_URL_DEPTH}/{symbol}", json={"token": API_TOKEN, "data": data})
                
                if res.status_code == 200:
                    print("✅ BAŞARILI!")
                else:
                    print(f"❌ HATA: {res.text}")
            else:
                print("⚠️ Kopyalanan veri Matriks formatına benzemiyor (Sekme ayracı yok).")
                
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        
    time.sleep(1)
