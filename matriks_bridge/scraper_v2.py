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
    """Windows focus kilidini kır."""
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
    """MatriksIQ pencere handle'ını bul."""
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
        """Sembolu eSymbol kutusuna yaz."""
        self._focus()
        time.sleep(0.3)
        
        # ESC tuşuna basarak önceki işlemi iptal et
        pyautogui.press('esc', presses=2)
        time.sleep(0.3)
        
        print(f"[2] Sembol yazılıyor: {symbol}")
        
        # eSymbol butonunun yanındaki kutu - koordinat ile tıklayıp yaz
        # Debug'dan: eSymbol x=1014, Edit x=1018, y=104
        # Sembol kutusu: x=690, y=99, w=247, h=29 (daha büyük olan)
        
        # İlk olarak pencereye tıkla
        r = self.main_win.rectangle()
        pyautogui.click(r.left + 50, r.top + 50)
        time.sleep(0.2)
        
        # Ctrl+A ve Backspace ile temizle
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('backspace')
        time.sleep(0.1)
        
        # Sembolü yaz
        pyautogui.write(symbol.upper(), interval=0.05)
        time.sleep(0.3)
        
        # Enter ile gönder
        pyautogui.press('enter')
        
        # Verinin yüklenmesini bekle
        time.sleep(4.0)
        print(f"[2] '{symbol}' yazıldı")

    def _click_button_by_name(self, button_name):
        """Belirli bir butona tıkla (koordinat ile)."""
        buttons = {
            "eSymbol": (1014, 99),
            "Derinlik": (1148, 99),
            "Grafik": (1181, 99),
            "AKD": (1248, 99),
            "Klasik": (1282, 99),
        }
        
        if button_name in buttons:
            x, y = buttons[button_name]
            print(f"[3] Butona tıklanıyor: {button_name} ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(0.2)
            return True
        return False

    def _press_hotkey(self, hotkey):
        """F tuşuna bas."""
        pyautogui.press(hotkey)
        print(f"[3] {hotkey} basıldı")
        time.sleep(0.5)

    def _wait_for_panel(self, timeout=5):
        """Yeni bir pencerenin açılmasını bekle."""
        time.sleep(timeout)
        
        # Masaüstündeki pencereleri kontrol et
        all_windows = []
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 2 and "MatriksIQ" not in title:
                    all_windows.append((hwnd, title))
        win32gui.EnumWindows(cb, None)
        
        return all_windows

    def _capture_screen(self, output_path):
        """Ekran görüntüsü al."""
        try:
            # Önce ana pencereyi bul
            r = self.main_win.rectangle()
            
            # Matriks verileri geç gelebilir, bekle
            time.sleep(1.5)
            
            # Ekran görüntüsü al
            img = pyautogui.screenshot(region=(r.left, r.top, r.width(), r.height()))
            img.save(output_path)
            print(f"[4] Ekran görüntüsü alındı: {output_path}")
            return True
        except Exception as e:
            print(f"[4] Hata: {e}")
            return False

    def run(self, symbol, hotkey, output_path):
        """
        Ana fonksiyon:
        1. Matriks'e odaklan
        2. Sembolü yaz
        3. F tuşuna bas veya butona tıkla
        4. Ekran görüntüsü al
        """
        try:
            # [1] Odaklan
            self._focus()
            time.sleep(0.5)

            # [2] Sembol yaz
            self._type_symbol(symbol)
            
            # [3] F tuşuna bas (hotkey F1, F2, F3, F4 vb.)
            self._press_hotkey(hotkey)
            
            # Pencerenin açılmasını bekle
            time.sleep(3)
            
            # [4] Ekran görüntüsü al
            print("[4] Ekran görüntüsü alınıyor...")
            self._capture_screen(output_path)
            
            # [5] Temizlik - ESC tuşuna bas
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
        print("Kullanım: scraper_v2.py <SYMBOL> <HOTKEY> <OUTPUT_PATH>")
        print("Örnek: scraper_v2.py THYAO f1 data/matriks/THYAO_Derinlik.png")
        sys.exit(1)

    symbol = sys.argv[1]
    hotkey = sys.argv[2].lower()
    output_path = sys.argv[3]

    print(f"=== Matriks Scraper v2 ===")
    print(f"Sembol: {symbol} | Hotkey: {hotkey} | Çıktı: {output_path}")

    # Hotkey'i düzelt
    if not hotkey.startswith('f'):
        hotkey = 'f' + hotkey

    scraper = MatriksScraper()
    ok = scraper.run(symbol, hotkey, output_path)

    if ok:
        print("BASARILI")
        sys.exit(0)
    else:
        print("BASARISIZ")
        sys.exit(1)
