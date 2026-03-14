import pywinauto
from pywinauto import Desktop
import sys
import io

# UTF-8 ayarı
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def dump_matriks_tree():
    print("--- MatriksIQ Pencere Ağacı Dökülüyor ---")
    try:
        # Masaüstündeki tüm pencereleri tara
        windows = Desktop(backend="uia").windows()
        matriks_win = None
        for win in windows:
            if "MatriksIQ" in win.window_text():
                matriks_win = win
                break
        
        if not matriks_win:
            print("HATA: MatriksIQ bulunamadı!")
            return

        print(f"Bulunan Ana Pencere: {matriks_win.window_text()}")
        
        # Pencere içindeki tüm kontrol elemanlarını dök
        # Bu işlem çok uzun sürebilir, derinliği sınırlıyoruz veya sadece Edit/Arama alanlarını arıyoruz
        with open("matriks_ui_dump.txt", "w", encoding="utf-8") as f:
            # print_control_identifiers() çıktısını dosyaya yönlendir
            sys.stdout = f
            matriks_win.print_control_identifiers()
            sys.stdout = sys.__stdout__
        
        print("BAŞARILI: matriks_ui_dump.txt dosyasına yazıldı.")
        
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    dump_matriks_tree()
