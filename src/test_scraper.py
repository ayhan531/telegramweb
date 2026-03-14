import sys
import os
import time

# Proje kök dizinini ekle
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from matriks_bridge.universal_scraper import MatriksScraper

def test():
    symbol = "THYAO"
    hotkey = "f1" # Derinlik
    menu_text = "Kademe Analizi"
    output = os.path.join(root, "data", "test_capture.png")
    
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    print(f"Test basliyor: {symbol} için {menu_text} cekilecek...")
    scraper = MatriksScraper()
    success = scraper.run(symbol, hotkey, menu_text, output)
    
    if success and os.path.exists(output):
        print(f"BASARILI! Görüntü kaydedildi: {output}")
    else:
        print("BASARISIZ! MatriksIQ acik mi? Ekran kilitli mi?")

if __name__ == "__main__":
    test()
