import pywinauto
from pywinauto import Desktop

def analyze_win():
    print("🔍 Matriks penceresi analiz ediliyor...")
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=".*MatriksIQ Session Exists.*")
        win = app.top_window()
        print(f"Title: {win.texts()}")
        # win.print_control_identifiers()
        # Usually it means 'Another session found' or something.
        # Let's try to just click 'OK' or 'Enter'
        win.type_keys("{ENTER}")
        print("✅ Otomatik 'ENTER' basıldı (Session Exists geçildi).")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    analyze_win()
