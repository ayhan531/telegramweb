import pyautogui
import os

def take_shot():
    print("📸 Ekran görüntüsü alınıyor...")
    try:
        shot = pyautogui.screenshot()
        shot.save("matriks_state.png")
        print("✅ Kaydedildi: matriks_state.png")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    take_shot()
