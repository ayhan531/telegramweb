import pywinauto
from pywinauto import Desktop

def dump_controls():
    print("🔍 Matriks Penceresi Detay Analizi...")
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=".*Matriks.*")
        win = app.top_window()
        # win.print_control_identifiers()
        # I'll only list some buttons/menus for brevity
        controls = win.descendants(control_type="MenuItem")
        for c in controls:
            print(f"- Menü Item: {c.window_text()}")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    dump_controls()
