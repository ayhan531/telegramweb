import pywinauto
import psutil

def dump_by_pid():
    pids = [p.info['pid'] for p in psutil.process_iter(['name', 'pid']) if 'MatriksIQ' in p.info['name']]
    if not pids:
        print("MatriksIQ process not found.")
        return
    
    print(f"🔍 PID {pids[0]} üzerinden kontrol ediliyor...")
    app = pywinauto.Application(backend="uia").connect(process=pids[0])
    win = app.top_window()
    print(f"Pencere: {win.texts()}")
    
    # Menü ve Butonları listele
    print("📋 Menüler:")
    for item in win.descendants(control_type="MenuItem"):
        print(f" - {item.window_text()}")

if __name__ == "__main__":
    dump_by_pid()
