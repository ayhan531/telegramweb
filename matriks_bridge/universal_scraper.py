import time
import sys
import os
import io
import pyautogui
from pywinauto import Application, Desktop
import win32gui
import win32con
import ctypes

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

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
            if "MatriksIQ" in title:
                result.append((hwnd, title))
    win32gui.EnumWindows(cb, None)
    return result[0] if result else None


def snapshot_all_descendants(main_win):
    """Ana penceredeki tüm child'ların text+rect bilgisini döndür."""
    items = []
    try:
        for child in main_win.descendants():
            try:
                txt = child.window_text()
                r = child.rectangle()
                area = r.width() * r.height()
                if txt and area > 20000:
                    items.append({
                        'text': txt,
                        'left': r.left, 'top': r.top,
                        'w': r.width(), 'h': r.height(),
                        'area': area,
                        'obj': child
                    })
            except:
                pass
    except:
        pass
    return items


class MatriksScraper:
    def __init__(self):
        self.app = None
        self.main_win = None
        self.hwnd = None
        self._connect()

    def _connect(self):
        print("[1] Matriks IQ bulunuyor...")
        # Birden fazla pencere varsa en üsttekini al
        try:
            self.app = Application(backend="uia").connect(title_re=".*MatriksIQ.*", timeout=10)
            self.main_win = self.app.window(title_re=".*MatriksIQ.*", found_index=0)
        except:
            # Fallback to handle by class if possible
            self.app = Application(backend="uia").connect(class_name="Window", title_re=".*MatriksIQ.*", timeout=10)
            self.main_win = self.app.window(title_re=".*MatriksIQ.*", found_index=0)
            
        found = find_matriks_hwnd()
        if found:
            self.hwnd = found[0]
            force_foreground(self.hwnd)
        else:
            self.main_win.set_focus()
        time.sleep(0.5)
        print("[1] Matriks IQ odaklandi OK")

    def _focus(self):
        if self.hwnd:
            force_foreground(self.hwnd)
        try:
            self.main_win.set_focus()
        except:
            pass
        time.sleep(0.3)

    def _type_symbol(self, symbol):
        """Matriks'te SearchEdit kontrolünü bul ve sembolü yaz."""
        self._focus()
        time.sleep(0.5)
        pyautogui.press('esc', presses=3)
        time.sleep(0.5)
        
        print(f"[2] Sembol degistiriliyor: {symbol}")
        try:
            # En sağlam yol: SearchEdit kontrolünü UIA ile bul
            search = self.main_win.child_window(auto_id="SearchEdit", control_type="Edit")
            search.click_input()
            time.sleep(0.3)
            
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            time.sleep(0.2)
            
            pyautogui.write(symbol.upper(), interval=0.05)
            time.sleep(0.3)
            pyautogui.press('enter')
            time.sleep(5.0) # Verinin tam yüklenmesi
            print(f"[2] '{symbol}' aktif sembol yapildi OK")
        except Exception as e:
            print(f"[2] SearchEdit bulunamadi, manuel deneme: {e}")
            # Koordinat ile dene (farklı çalışma alanlarında yer değişebilir)
            r = self.main_win.rectangle()
            pyautogui.click(r.right - 150, r.top + 15)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(symbol.upper())
            pyautogui.press('enter')
            time.sleep(5.0)

    def _press_hotkey(self, hotkey):
        """F tuşuna veya Alt+G'ye bas."""
        if hotkey == 'altg':
            pyautogui.hotkey('alt', 'g')
            print("[3] Alt+G basildi OK")
        else:
            pyautogui.press(hotkey)
            print(f"[3] {hotkey.upper()} basildi OK")

    def _find_new_panel(self, before_snapshot, symbol, menu_text):
        """
        F tuşu öncesi ve sonrası child listesini karşılaştırarak
        yeni açılan paneli bul.
        """
        after = snapshot_all_descendants(self.main_win)
        before_texts = set(item['text'] for item in before_snapshot)
        
        # Yeni veya ismi değişmiş pencereleri ara
        candidates = []
        for item in after:
            # Sembol veya Menü Metni içeriyorsa en güçlü adaydır
            txt = item['text'].lower()
            if (symbol.lower() in txt or (menu_text and menu_text.lower() in txt)) and item['area'] > 20000:
                candidates.append(item)
            elif item['text'] not in before_texts and item['area'] > 40000:
                candidates.append(item)
        
        if candidates:
            # En son eklenen veya en büyük olanı al
            candidates.sort(key=lambda x: x['area'], reverse=True)
            best = candidates[0]
            print(f"[4] Panel SORGUSU basarili: '{best['text'][:40]}'")
            return best['obj']
        
        return None

    def _right_click_select(self, panel, menu_text):
        """
        Panel üzerinde sağ tıkla, açılan menüden menu_text'i seç.
        """
        rect = panel.rectangle()
        cx = rect.left + rect.width() // 2
        cy = rect.top + rect.height() // 2
        
        # Sol tıkla odaklan
        pyautogui.click(cx, cy)
        time.sleep(0.4)
        
        # Sağ tıkla
        pyautogui.rightClick(cx, cy)
        time.sleep(1.5)
        
        # Context menüdeki item'ı bul
        found = self._find_context_item(menu_text)
        if found:
            print(f"[5] Menu ogesi '{menu_text}' bulundu, tiklaniyor")
            try:
                found.click_input()
            except:
                try:
                    mr = found.rectangle()
                    pyautogui.click(mr.left + mr.width()//2, mr.top + mr.height()//2)
                except:
                    pass
            return True
        else:
            print(f"[5] Menu ogesi '{menu_text}' bulunamadi, klavye ile seciliyor...")
            # Menü açıkken ilk harfi yazarak seçme (Matriks menüsü bunu destekler)
            first_char = menu_text[0].lower()
            pyautogui.press(first_char)
            time.sleep(0.3)
            pyautogui.press('enter')
            return True

    def _find_context_item(self, text):
        """Masaüstündeki açık context menüde text'i ara."""
        text_lower = text.lower()
        for win in Desktop(backend="uia").windows():
            try:
                cn = win.class_name()
                # WPF/Win32 context menüler
                if cn in ['#32768', 'Popup', 'ContextMenu', 'DropDown', '']:
                    for item in win.descendants():
                        try:
                            it = item.window_text()
                            if it and text_lower in it.lower():
                                return item
                        except:
                            pass
            except:
                pass
        return None

    def _capture(self, panel, output_path):
        """Panelin ekran görüntüsünü al."""
        try:
            # Panel varsa sadece o bölgeyi al
            target_rect = None
            if panel:
                try:
                    r = panel.rectangle()
                    target_rect = (r.left, r.top, r.width(), r.height())
                except: pass
            
            if not target_rect:
                # Panel yoksa ana pencereyi al
                r = self.main_win.rectangle()
                target_rect = (r.left, r.top, r.width(), r.height())
            
            # Matriks verileri bazen geç dolar, 1 saniye daha bekleyelim
            time.sleep(1.5)
            img = pyautogui.screenshot(region=target_rect)
            img.save(output_path)
            print(f"[6] Ekran goruntusu alindi: {output_path} OK")
            return True
        except Exception as e:
            print(f"[6] Screenshot hatasi: {e}")
            try:
                pyautogui.screenshot().save(output_path)
                return True
            except:
                return False

    def _cleanup(self):
        """Açılan panelleri kapat."""
        self._focus()
        time.sleep(0.3)
        # Ctrl+F4 ile sekme/panel kapat
        pyautogui.hotkey('ctrl', 'f4')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'f4')
        time.sleep(0.3)
        pyautogui.press('escape', presses=3)
        time.sleep(0.3)
        print("[7] Temizlik OK")

    # =====================================================
    # ANA FONKSİYON
    # =====================================================
    def run(self, symbol, hotkey, menu_text, output_path):
        """
        7 adimda veri yakala:
        1. Matriks'e odaklan
        2. Sembolü yaz
        3. F tuşuna bas
        4. Yeni açılan paneli bul
        5. Sağ tıkla → menüden seç
        6. Ekran görüntüsü al
        7. Temizle
        """
        try:
            # [1] Odaklan
            self._focus()

            # [2] Sembol yaz
            self._type_symbol(symbol)

            # [3] F tuşundan önceki durumu kaydet
            print("[3] Hotkey oncesi durum kaydediliyor...")
            before = snapshot_all_descendants(self.main_win)
            self._focus()
            self._press_hotkey(hotkey)
            time.sleep(3)  # Pencerenin açılması için bekle

            # [4] Yeni açılan paneli bul
            panel = self._find_new_panel(before, symbol, menu_text)

            if not panel:
                # Panel bulunamadiysa sag tikla deneyelim
                print(f"[4] Panel henuz bulunamadi, sag tik ile '{menu_text}' denenecek...")
                # Ana pencere ortasina tikla odaklan
                r = self.main_win.rectangle()
                pyautogui.click(r.left + r.width()//2, r.top + r.height()//2)
                time.sleep(0.3)
                pyautogui.rightClick()
                time.sleep(1.5)
                
                self._right_click_select(self.main_win, menu_text) # Ana pencere uzerinde ara
                time.sleep(3)
                panel = self._find_new_panel(before, symbol, menu_text)

            # [6] Ekran görüntüsü al
            print("[6] Ekran goruntusu aliniyor...")
            time.sleep(1.5)
            self._capture(panel, output_path)

            # [7] Temizle
            self._cleanup()
            return True

        except Exception as e:
            import traceback
            print(f"HATA: {e}")
            traceback.print_exc()
            try: self._cleanup()
            except: pass
            return False


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Kullanim: universal_scraper.py <SYMBOL> <HOTKEY> <MENU_TEXT> <OUTPUT_PATH>")
        sys.exit(1)

    symbol = sys.argv[1]
    hotkey = sys.argv[2]
    menu_text = sys.argv[3]
    output_path = sys.argv[4]

    print(f"=== Matriks Scraper ===")
    print(f"Sembol: {symbol} | Hotkey: {hotkey} | Menu: {menu_text}")

    scraper = MatriksScraper()
    ok = scraper.run(symbol, hotkey, menu_text, output_path)

    if ok:
        print("BASARILI")
        sys.exit(0)
    else:
        print("BASARISIZ")
        sys.exit(1)
