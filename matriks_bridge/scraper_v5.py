import time
import sys
import os
import pyautogui
from pywinauto import Application, Desktop
import win32gui
import win32con
import ctypes

pyautogui.PAUSE = 0.05
pyautogui.FAILSAFE = False


def force_foreground(hwnd):
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        shell = ctypes.windll.user32
        shell.keybd_event(0xA4, 0x38, 0, 0)
        shell.keybd_event(0xA4, 0x38, 2, 0)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
    except:
        pass


def find_matriks_hwnd():
    result = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "MatriksIQ Veri Terminali" in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(cb, None)
    return result[0] if result else None


class MatriksScraper:
    def __init__(self):
        self.app = None
        self.main_win = None
        self.hwnd = None
        self._connect()

    def _connect(self):
        print("[1] MatriksIQ bağlanıyor...")
        try:
            self.app = Application(backend="uia").connect(title_re=".*MatriksIQ Veri Terminali.*", timeout=10)
            self.main_win = self.app.window(title_re=".*MatriksIQ Veri Terminali.*")
        except:
            self.app = Application(backend="uia").connect(class_name="Window", title_re=".*MatriksIQ.*", timeout=10)
            self.main_win = self.app.window(title_re=".*MatriksIQ.*")
            
        found = find_matriks_hwnd()
        if found:
            self.hwnd = found[0]
            force_foreground(self.hwnd)
        else:
            self.main_win.set_focus()
        time.sleep(0.5)
        print("[1] MatriksIQ bağlandı")

    def _focus(self):
        if self.hwnd:
            force_foreground(self.hwnd)
        try:
            self.main_win.set_focus()
        except:
            pass
        time.sleep(0.3)

    def _type_symbol(self, symbol):
        """Sembolu direkt klavye ile yaz (Arama kutusu odağına güvenmeden)."""
        self._focus()
        time.sleep(1.0)
        
        # ESC ile varsa açık pencereleri/menüleri kapat
        pyautogui.press('esc', presses=2)
        time.sleep(0.5)
        
        print(f"[2] Sembol yazılıyor: {symbol}")
        
        # MatriksIQ'da bazen 'period' (nokta) tuşu arama kutusunu açar
        # veya direkt yazmaya başlamak yeterlidir.
        # En garanti yol: Tüm seçimleri iptal et ve temiz bir başlangıç yap.
        pyautogui.press('esc')
        time.sleep(0.2)
        
        # Görselde üst barın solunda 'EREGL' yazan yer (137, 55) koordinatlarında.
        pyautogui.click(137, 55) 
        time.sleep(0.3)
        
        # Mevcut yazıyı temizlemek için Ctrl+A ve Backspace
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('backspace')
        time.sleep(0.2)
        
        # Sembolü yaz
        pyautogui.write(symbol.upper(), interval=0.1)
        time.sleep(0.5)
        
        # Enter ile ara
        pyautogui.press('enter')
        
        # Yüklenmesini bekle (Sembol değişimi zaman alabilir)
        time.sleep(3.0)
        print(f"[2] '{symbol}' yazıldı")

    def _right_click_and_select(self, menu_item, action):
        """Kısayol tuşlarını kullan veya sağ tıkla."""
        self._focus()
        
        # Kısayol tuşları daha güvenlidir
        hotkeys = {
            "derinlik": "f2",  # Matriks'te derinlik genelde F2'dir
            "akd": "f3",       # AKD genelde F3'tür
            "grafik": "f11",   # Grafik genelde F11 veya G harfidir
        }
        
        act_key = action.lower()
        if act_key in hotkeys:
            print(f"[3] Kısayol basılıyor: {hotkeys[act_key]}")
            pyautogui.press(hotkeys[act_key])
            time.sleep(2.0)
            return

        # Kısayol yoksa sağ tık metoduna dön
        r = self.main_win.rectangle()
        center_x = r.left + (r.width() // 2)
        center_y = r.top + (r.height() // 3)
        
        print(f"[4] Sağ tık yapılıyor ({center_x}, {center_y})...")
        pyautogui.rightClick(center_x, center_y)
        time.sleep(1.0)
        
        print(f"[5] Menüden '{menu_item}' seçiliyor...")
        pyautogui.write(menu_item[0].lower())
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(2.0)

    def _capture_screen(self, output_path):
        """Ekran görüntüsü al."""
        try:
            r = self.main_win.rectangle()
            time.sleep(1.0)
            img = pyautogui.screenshot(region=(r.left, r.top, r.width(), r.height()))
            img.save(output_path)
            print(f"[6] Ekran görüntüsü: {output_path}")
            return True
        except Exception as e:
            print(f"[6] Hata: {e}")
            return False

    def run(self, symbol, action, output_path):
        try:
            self._focus()
            time.sleep(0.5)

            # Sembol yaz
            self._type_symbol(symbol)
            
            # Menü seçenekleri
            menu_options = {
                "derinlik": "Kademe Analizi",
                "akd": "Aracı Kurum Dağılımı",
                "grafik": "Grafik",
                "takas": "Takas",
            }
            
            menu_item = menu_options.get(action.lower(), action)
            self._right_click_and_select(menu_item, action)
            
            # Ekran görüntüsü
            print("[6] Ekran görüntüsü alınıyor...")
            self._capture_screen(output_path)
            
            # Temizlik
            pyautogui.press('esc')
            time.sleep(0.3)
            
            return True
            
        except Exception as e:
            import traceback
            print(f"HATA: {e}")
            traceback.print_exc()
            return False


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Kullanım: scraper_v5.py <SYMBOL> <ACTION> <OUTPUT_PATH>")
        print("Örnek: scraper_v5.py THYAO derinlik data/matriks/THYAO.png")
        sys.exit(1)

    symbol = sys.argv[1]
    action = sys.argv[2]
    output_path = sys.argv[3]

    print(f"=== Matriks Scraper v5 ===")
    print(f"Sembol: {symbol} | İşlem: {action}")

    scraper = MatriksScraper()
    ok = scraper.run(symbol, action, output_path)

    print("BASARILI" if ok else "BASARISIZ")
    sys.exit(0 if ok else 1)
