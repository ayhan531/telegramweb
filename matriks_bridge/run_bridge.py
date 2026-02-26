import time
import requests
import json
import pyperclip

# --- AYARLAR ---
API_URL = "https://telegramweb-gd62.onrender.com/api/push-matriks-akd"
API_TOKEN = "MATRIKS_GIZLI_TOKEN_123" # .env'ye de aynı tokeni eklemelisiniz

print("========================================")
print(" MATRİKS -> RENDER (TELEGRAM) KÖPRÜSÜ ")
print("========================================")
print("Bu program arka planda çalışır. Matriks'ten herhangi bir")
print("Aracı Kurum Dağılımı (AKD) tablosunu KOPYALADIĞINIZDA (Ctrl+C),")
print("otomatik olarak algılar ve buluttaki bota gönderir.\n")

last_clipboard = ""

def parse_matriks_akd_clipboard(text):
    """
    Kopyalanan Matriks tablosunu analiz eder ve JSON'a çevirir.
    Basit bir ayrıştırma: Sekme (\t) ile ayrılmış kolonlar.
    """
    lines = text.strip().split('\n')
    buyers = []
    sellers = []
    
    # Çok temel bir ayrıştırma (Matriks sekme ayrımını kullanır)
    # Satır düzeni genelde: Kurum, Lot, Maliyet, Pay
    for line in lines:
        cols = line.split('\t')
        if len(cols) >= 3:
            kurum = cols[0].strip()
            lot = cols[1].strip()
            # Basit bir kontrol, eğer lot rakam ise:
            if lot.replace('.', '').replace(',', '').isdigit():
                # Kurum adına göre alan veya satan olduğunu belirleme vb. gerekebilir
                # Matriks'in kopyalama dizilimine göre buraya daha gelişmiş filtre eklenebilir.
                # Örnek olarak ilk 10 satırı alan, sonraki 10'u satan farz ediyoruz veya 
                # lot değerinin büyüklüğüne göre sıralıyoruz.
                buyers.append({
                    "kurum": kurum[:20],
                    "lot": lot,
                    "pay": 0, # İhtiyaç halinde eklenebilir
                    "maliyet": "---"
                })
                
    # Bu basit bir taslaktır. Matriks'ten kopyaladığınız verinin tam formatına
    # göre buradaki split işlemleri revize edilmelidir (Örn: 'Alıcılar' ve 'Satıcılar' başlıkları).
    
    # Şu anlık her şeyi alıcılara koyup temsili gönderiyoruz
    return {
        "buyers": buyers[:5],
        "sellers": buyers[5:10] if len(buyers)>5 else [],
        "total": [],
        "source": "Matriks Terminal (Canlı DDE/Kopya)",
        "status": "Gerçek Veri"
    }

while True:
    try:
        current_clipboard = pyperclip.paste()
        
        # Eğer panoda yeni bir şeye rastlarsak ve matriks formatına benziyorsa
        if current_clipboard != last_clipboard and "Kurum" in current_clipboard and "%" in current_clipboard:
            last_clipboard = current_clipboard
            
            # Hangi hisse olduğunu anlamak için manuel giriş veya yazıdan çekme
            # Şimdilik konsoldan soralım:
            print("\n*** Yeni AKD Algılandı! ***")
            symbol = input("Bu veriler hangi hisseye ait? (Örn: THYAO): ").strip().upper()
            
            if symbol:
                parsed_data = parse_matriks_akd_clipboard(current_clipboard)
                
                payload = {
                    "token": API_TOKEN,
                    "data": parsed_data
                }
                
                print(f"-> {symbol} verileri sunucuya gönderiliyor...")
                response = requests.post(f"{API_URL}/{symbol}", json=payload)
                
                if response.status_code == 200:
                    print("BAŞARILI: Veri Telegram Botuna Ulaştı!")
                else:
                    print("HATA:", response.text)
            
    except Exception as e:
        print("Beklenmeyen hata:", e)
        
    time.sleep(2) # 2 saniyede bir panoyu kontrol et
