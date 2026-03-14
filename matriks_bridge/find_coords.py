import pyautogui
import time
import sys

def get_mouse_pos():
    print("5 saniye içinde farenizi MatriksIQ'daki sembol yazma kutusunun (EREGL yazan yer) üzerine getirin...")
    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    pos = pyautogui.position()
    print(f"\nSeçilen Koordinat: X={pos.x}, Y={pos.y}")
    print(f"Lütfen bu koordinatları scraper_v5.py içindeki pyautogui.click() kısmına yazın.")

if __name__ == "__main__":
    get_mouse_pos()
