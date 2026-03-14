import time
from pywinauto import Application
from PIL import Image

class MatriksKademeScraper:
    def __init__(self):
        self.app = None
        self.main_win = None
        self.connect()

    def connect(self):
        try:
            self.app = Application(backend="uia").connect(title_re=".*MatriksIQ.*")
            self.main_win = self.app.window(title_re=".*MatriksIQ Veri Terminali.*")
            
            # Eğer simge durumundaysa büyüt
            try:
                if self.main_win.get_show_state() == 2:
                    self.main_win.restore()
            except: pass
            
            self.main_win.set_focus()
            print("✅ MatriksIQ'ya bağlandım.")
        except Exception as e:
            print(f"❌ Bağlantı hatası: {e}")

    def capture_kademe(self, symbol, output_path="final_kademe.png"):
        try:
            # 1. Kademe Analizi penceresini ara (Hem iç hem dış)
            def find_window():
                # Önce ana pencere içinde ara
                for child in self.main_win.descendants():
                    try:
                        if "Kademe Analizi" in child.window_text():
                            return child
                    except: continue
                # Sonra masaüstünde ara
                from pywinauto import Desktop
                for win in Desktop(backend="uia").windows():
                    try:
                        if "Kademe Analizi" in win.window_text():
                            return win
                    except: continue
                return None

            kademe_win = find_window()
            
            if not kademe_win:
                print("⚠️ Kademe Analizi açık değil, açılmaya çalışılıyor...")
                self.main_win.set_focus()
                # Sembol yaz ve Enter bas (Detay penceresini açar veya günceller)
                self.main_win.type_keys("^a{BACKSPACE}" + symbol + "{ENTER}{ENTER}")
                time.sleep(2)
                # 'k' tuşu genellikle Kademe Analizi'ni açar (Detay penceresi odaklıyken)
                self.main_win.type_keys("k")
                time.sleep(2)
                kademe_win = find_window()

            if not kademe_win:
                # F2 son şans
                self.main_win.type_keys("{F2}")
                time.sleep(2)
                kademe_win = find_window()

            if not kademe_win:
                print("❌ Kademe Analizi penceresi hala bulunamadı!")
                return False

            # 2. Kademe penceresine odaklan
            print(f"🎯 {symbol} için Kademe penceresi güncelleniyor...")
            kademe_win.set_focus()
            time.sleep(1)
            
            # Click inside to activate
            rect = kademe_win.rectangle()
            from pywinauto import mouse
            mouse.click(coords=(rect.left + 50, rect.top + 80))
            time.sleep(0.5)

            # Type symbol and enter
            # Matriks'te pencere odaklıyken direkt yazınca sembol değişir
            self.main_win.type_keys("^a{BACKSPACE}" + symbol + "{ENTER}{ENTER}")
            time.sleep(3)
            
            # 3. Yakala
            print(f"📸 {symbol} Kademe Analizi yakalanıyor...")
            kademe_win.capture_as_image().save(output_path)
            print(f"✅ Başarılı: {output_path}")
            return True
                
        except Exception as e:
            print(f"Hata: {e}")
            return False

if __name__ == "__main__":
    scraper = MatriksKademeScraper()
    scraper.capture_kademe("GARAN", "garan_kademe_test.png")
