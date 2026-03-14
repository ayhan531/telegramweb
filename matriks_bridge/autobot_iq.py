import pywinauto
import time
import subprocess
import os

# Ayarlar
EXE_PATH = r"c:\Users\Cem\Desktop\derinlikbot\MatriksIQ\MatriksIQ\MatriksIQ.exe"
USER = "43719"
PASS = "RZpGH717"

def start_and_login():
    print(f"🚀 MatriksIQ başlatılıyor: {EXE_PATH}")
    
    # Uygulamayı başlat
    subprocess.Popen(EXE_PATH)
    
    # Pencerenin gelmesini bekle (Başlangıç süresi uzun olabilir)
    print("⏳ Giriş penceresi bekleniyor (30 saniye)...")
    time.sleep(30)
    
    try:
        app = pywinauto.Application(backend="win32").connect(title_re=".*Matriks.*", timeout=10)
        main_win = app.top_window()
        print(f"✅ Pencere bulundu: {main_win.texts()}")
        
        # Giriş alanlarını bulmaya ve doldurmaya çalış (Otomatik)
        # Not: MatriksIQ modern bir UI (WPF) kullandığı için 'win32' backend'i yetmeyebilir
        # 'uia' backend'i daha iyi sonuç verebilir.
        
        # Eğer pencere başlığı 'Giriş' veya 'Login' ise:
        # main_win.type_keys(USER + "{TAB}" + PASS + "{ENTER}")
        
    except Exception as e:
        print(f"❌ Pencere bulunamadı veya bir hata oluştu: {e}")
        print("💡 Lütfen şu an ekranına bak, MatriksIQ açıldı mı? Eğer açıldıysa giriş bilgilerini denerim.")

if __name__ == "__main__":
    start_and_login()
