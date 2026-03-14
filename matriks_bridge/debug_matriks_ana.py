import sys
from pywinauto import Application, Desktop
import win32gui
import time

def main():
    print("=" * 60)
    print("MATRIKS IQ VERI TERMINALI DETAYLI ANALIZ")
    print("=" * 60)
    
    # pywinauto ile bağlan
    try:
        app = Application(backend="uia").connect(title_re=".*MatriksIQ Veri Terminali.*", timeout=10)
        win = app.window(title_re=".*MatriksIQ Veri Terminali.*")
        win.set_focus()
        time.sleep(0.5)
        
        hwnd = win.handle
        print(f"Pencere bulundu! HWND: {hwnd}")
        
        print("\n" + "=" * 60)
        print("EDIT KONTROLLERİ (Sembol giriş kutuları)")
        print("=" * 60)
        
        edit_count = 0
        for ctrl in win.descendants(control_type="Edit"):
            try:
                rect = ctrl.rectangle()
                name = ctrl.window_text()
                edit_count += 1
                print(f"\n  [{edit_count}] Edit: '{name}'")
                print(f"    Konum: x={rect.left}, y={rect.top}, w={rect.width()}, h={rect.height()}")
                print(f"    Class: {ctrl.get_class_name()}")
            except Exception as e:
                print(f"  Hata: {e}")
        
        print(f"\nToplam Edit sayısı: {edit_count}")
        
        print("\n" + "=" * 60)
        print("BUTTON'LAR (Özellikle üst menü)")
        print("=" * 60)
        
        # Üst kısımdaki butonları bul (y koordinatı küçük olanlar)
        buttons = []
        for ctrl in win.descendants(control_type="Button"):
            try:
                name = ctrl.window_text()
                if name and len(name) > 0:
                    rect = ctrl.rectangle()
                    buttons.append((rect.top, name, rect.left, rect.top, rect.width(), rect.height()))
            except:
                pass
        
        # Y'ye göre sırala
        buttons.sort()
        print("\nÜst menü butonları (yukarıdan aşağıya):")
        for y, name, x, y2, w, h in buttons[:30]:
            print(f"  y={y:4} | x={x:4} | '{name[:25]}'")
        
        print("\n" + "=" * 60)
        print("PANE/WINDOW (Büyük pencereler)")
        print("=" * 60)
        
        for ctrl in win.descendants(control_type="Pane"):
            try:
                name = ctrl.window_text()
                if name and len(name) > 3:
                    rect = ctrl.rectangle()
                    if rect.width() > 200 and rect.height() > 100:
                        print(f"\n  Panel: '{name[:60]}'")
                        print(f"    Konum: x={rect.left}, y={rect.top}, w={rect.width()}, h={rect.height()}")
            except:
                pass
                
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
