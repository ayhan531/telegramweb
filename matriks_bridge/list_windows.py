import pywinauto
from pywinauto import Desktop

def list_windows():
    print("📋 Mevcut pencereler:")
    windows = Desktop(backend="uia").windows()
    for w in windows:
        if w.texts() and w.texts()[0]:
            print(f"- {w.texts()[0]}")

if __name__ == "__main__":
    list_windows()
