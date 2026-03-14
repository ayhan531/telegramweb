import sys
import os
import time

# Proje kök dizinini path'e ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matriks_bridge.scraper_v5 import MatriksScraper

def test_scraper():
    symbol = "THYAO"
    action = "derinlik"
    output_path = os.path.join("data", "matriks", "test_thyao_derinlik.png")
    
    # Klasörü oluştur
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"--- Scraper Test Başlatıldı ---")
    print(f"Sembol: {symbol} | İşlem: {action}")
    
    scraper = MatriksScraper()
    success = scraper.run(symbol, action, output_path)
    
    if success and os.path.exists(output_path):
        print(f"✅ TEST BAŞARILI: {output_path} oluşturuldu.")
    else:
        print(f"❌ TEST BAŞARISIZ.")

if __name__ == "__main__":
    test_scraper()
