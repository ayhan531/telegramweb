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
        """Sembolu eSymbol yanındaki kutuya yaz."""
        self._focus()
        time.sleep(0.3)
        
        # ESC tuşuna basarak önceki işlemi iptal et
        pyautogui.press('esc', presses=2)
        time.sleep(0.5)
        
        print(f"[2] Sembol yazılıyor: {symbol}")
        
        # eSymbol butonunun yanındaki kutuya tıkla
        # Debug'dan: eSymbol x=1014, Edit x=1018, y=104, w=125
        # Doğru kutu: x=1018, y=104 (sembol arama kutusu)
        pyautogui.click(1050, 112)  # eSymbol yanındaki kutuya tıkla
        time.sleep(0.3)
        
        # Temizle
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('backspace')
        time.sleep(0.1)
        
        # Sembolü yaz
        pyautogui.write(symbol.upper(), interval=0.08)
        time.sleep(0.3)
        
        # Enter ile ara
        pyautogui.press('enter')
        
        # Verinin yüklenmesini bekle
        time.sleep(4.0)
        print(f"[2] '{symbol}' yazıldı ve arandı")

    def _right_click_menu(self, menu_item):
        """Sağ tıkla ve menüden seç."""
        print(f"[3] Sağ tık menü açılıyor...")
        
        # Pencere ortasına sağ tıkla (F1/F2 sonrası açılan pencereye)
        r = self.main_win.rectangle()
        center_x = r.left + r.width() // 2
        center_y = r.top + r.height() // 2
        
        # Sağ tık
        pyautogui.rightClick(center_x, center_y)
        time.sleep(1.0)
        
        # Menü açıldı mı kontrol et ve öğeye tıkla
        # Menü öğelerini yazıya göre bul ve tıkla
        found = self._find_menu_item(menu_item)
        
        if found:
            print(f"[4] Menü öğesi bulundu: {menu_item}")
            time.sleep(0.3)
            pyautogui.press('enter')
        else:
            # Elle yaz (ilk harf)
            print(f"[4] Menü öğesi tıklanıyor: {menu_item}")
            pyautogui.write(menu_item[0].lower())  # İlk harf
            time.sleep(0.5)
            pyautogui.press('enter')
        
        time.sleep(2.0)  # Pencerenin açılmasını bekle

    def _find_menu_item(self, item_name):
        """Açık menüde öğe bul."""
        time.sleep(0.5)
        
        # Masaüstündeki popup pencereleri kontrol et
        for win in Desktop(backend="uia").windows():
            try:
                # Context menu genellikle #32768 class name
                if win.class_name() in ['#32768', 'Popup', 'ContextMenu']:
                    # İçindeki öğeleri kontrol et
                    for child in win.descendants():
                        try:
                            text = child.window_text()
                            if text and item_name.lower() in text.lower():
                                # Bulundu, tıkla
                                child.click_input()
                                return True
                        except:
                            pass
            except:
                pass
        return False

    def _capture_screen(self, output_path):
        """Ekran görüntüsü al."""
        try:
            r = self.main_win.rectangle()
            time.sleep(1.0)
            img = pyautogui.screenshot(region=(r.left, r.top, r.width(), r.height()))
            img.save(output_path)
            print(f"[5] Ekran görüntüsü alındı: {output_path}")
            return True
        except Exception as e:
            print(f"[5] Hata: {e}")
            return False

    def run(self, symbol, action, output_path):
        """
        Ana fonksiyon:
        1. Matriks'e odaklan
        2. Sembolü eSymbol kutusuna yaz ve ara
        3. F tuşuna bas
        4. Sağ tıkla ve menüden seç
        5. Ekran görüntüsü al
        
        action: derinlik, akd, grafik, takas
        """
        try:
            # [1] Odaklan
            self._focus()
            time.sleep(0.5)

            # [2] Sembol yaz ve ara
            self._type_symbol(symbol)
            
            # [3] F tuşuna bas
            f_key = "f1"  # Varsayılan derinlik
            if action.lower() == "akd":
                f_key = "f3"  # AKD için F3
            elif action.lower() == "grafik":
                f_key = "f4"  # Grafik için F4
            elif action.lower() == "takas":
                f_key = "f2"  # Takas için F2
                
            print(f"[3] {f_key} tuşuna basılıyor...")
            pyautogui.press(f_key)
            time.sleep(2.0)  # Pencerenin açılmasını bekle
            
            # [4] Sağ tık ve menüden seç
            menu_options = {
                "derinlik": "Kademe Analizi",
                "akd": "Aracı Kurum Dağılımı",
                "grafik": "Grafik",
                "takas": "Takas",
            }
            
            menu_item = menu_options.get(action.lower(), action)
            self._right_click_menu(menu_item)
            
            # [5] Ekran görüntüsü al
            print("[5] Ekran görüntüsü alınıyor...")
            self._capture_screen(output_path)
            
            # [6] Temizlik
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
        print("Kullanım: scraper_v4.py <SYMBOL> <ACTION> <OUTPUT_PATH>")
        print("ACTION: derinlik, akd, grafik, takas")
        print("Örnek: scraper_v4.py THYAO derinlik data/matriks/THYAO_Derinlik.png")
        sys.exit(1)

    symbol = sys.argv[1]
    action = sys.argv[2]
    output_path = sys.argv[3]

    print(f"=== Matriks Scraper v4 ===")
    print(f"Sembol: {symbol} | İşlem: {action} | Çıktı: {output_path}")

    scraper = MatriksScraper()
    ok = scraper.run(symbol, action, output_path)

    if ok:
        print("BASARILI")
        sys.exit(0)
    else:
        print("BASARISIZ")
        sys.exit(1)
