import sys
from pywinauto import Application, Desktop
import win32gui
import time

def print_hwnd_tree(hwnd, indent=0):
    """Rekursif olarak pencere ağacını yazdır"""
    try:
        if not win32gui.IsWindowVisible(hwnd):
            return
        
        title = win32gui.GetWindowText(hwnd)
        classname = win32gui.GetClassName(hwnd)
        
        if title:
            print("  " * indent + f"[{hwnd}] {classname}: {title[:60]}")
        
        # Child windows
        child = win32gui.GetWindow(hwnd, 5)  # GW_CHILD
        while child:
            print_hwnd_tree(child, indent + 1)
            child = win32gui.GetWindow(child, 2)  # GW_HWNDNEXT
    except:
        pass

def main():
    print("=" * 60)
    print("MATRIKS IQ PENCERE ANALIZI")
    print("=" * 60)
    
    # 1. MatriksIQ pencereyi bul
    matriks_windows = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Matriks" in title:
                matriks_windows.append((hwnd, title))
    win32gui.EnumWindows(cb, None)
    
    print(f"\nBulunan Matriks pencereleri: {len(matriks_windows)}")
    for hwnd, title in matriks_windows:
        print(f"  HWND: {hwnd} - {title}")
    
    if not matriks_windows:
        print("MatriksIQ bulunamadı! Lütfen önce MatriksIQ uygulamasını açın.")
        return
    
    # Ana pencereyi seç
    hwnd, main_title = matriks_windows[0]
    print(f"\nSeçilen pencere: {main_title}")
    print("\nPENCERE YAPISI (Hiyerarşi):")
    print("-" * 60)
    
    # Ana pencere ağacını yazdır
    print(f"[{hwnd}] Ana Pencere: {main_title}")
    child = win32gui.GetWindow(hwnd, 5)
    while child:
        print_hwnd_tree(child, 1)
        child = win32gui.GetWindow(child, 2)
    
    # 2. pywinauto ile daha detaylı analiz
    print("\n" + "=" * 60)
    print("PYWINAUTO DETAYLI KONTROL LİSTESİ")
    print("=" * 60)
    
    try:
        app = Application(backend="uia").connect(title_re=".*MatriksIQ.*", timeout=5)
        win = app.window(title_re=".*MatriksIQ.*")
        
        print(f"\nPencere kontrolleri (top-level):")
        for ctrl in win.descendants():
            try:
                ctrl_type = ctrl.control_type()
                ctrl_id = ctrl.auto_id()
                ctrl_name = ctrl.window_text()
                if ctrl_name and len(ctrl_name) > 0:
                    print(f"  {ctrl_type:20} | ID: {ctrl_id:25} | Text: {ctrl_name[:40]}")
            except:
                pass
        
        # 3. Edit kontrollerini özellikle bul
        print("\n" + "=" * 60)
        print("EDIT (Giriş Kutusu) KONTROLLERİ")
        print("=" * 60)
        for ctrl in win.descendants(control_type="Edit"):
            try:
                ctrl_id = ctrl.auto_id()
                ctrl_name = ctrl.window_text()
                rect = ctrl.rectangle()
                print(f"  Edit ID: {ctrl_id}")
                print(f"    Text: '{ctrl_name}'")
                print(f"    Konum: x={rect.left}, y={rect.top}, w={rect.width()}, h={rect.height()}")
            except Exception as e:
                print(f"  Hata: {e}")
        
        # 4. Button kontrolleri
        print("\n" + "=" * 60)
        print("BUTTON KONTROLLERİ")
        print("=" * 60)
        for ctrl in win.descendants(control_type="Button"):
            try:
                ctrl_name = ctrl.window_text()
                if ctrl_name:
                    rect = ctrl.rectangle()
                    print(f"  Button: '{ctrl_name[:30]}' | x={rect.left}, y={rect.top}")
            except:
                pass
                
    except Exception as e:
        print(f"pywinauto bağlantı hatası: {e}")
        print("MatriksIQ'nun açık olduğundan emin olun.")

if __name__ == "__main__":
    main()
    print("\nBitti. Çıkmak için Enter'a basın...")
    input()
