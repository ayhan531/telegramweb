import sys
import os
import time

# Proje kök dizinini ekle
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from matriks_bridge.universal_scraper import MatriksScraper

def run_test(symbol, hotkey, menu_text, test_name):
    output = os.path.join(root, "data", f"test_{test_name}.png")
    os.makedirs(os.path.dirname(output), exist_ok=True)
    
    print(f"\n>>> TEST: {test_name} ({symbol})")
    scraper = MatriksScraper()
    success = scraper.run(symbol, hotkey, menu_text, output)
    
    if success and os.path.exists(output):
        print(f"OK: {test_name} basarili. Dosya: {output}")
    else:
        print(f"HATA: {test_name} basarisiz.")

if __name__ == "__main__":
    # Sırayla testler
    run_test("THYAO", "f1", "Kademe Analizi", "derinlik")
    time.sleep(2)
    run_test("EREGL", "f3", "Aracı Kurum Dağılımı", "akd")
    time.sleep(2)
    run_test("GARAN", "f4", "Takas", "takas")
    time.sleep(2)
    run_test("SISE", "altg", "Grafik", "grafik")
