import pywinauto
import time

def login():
    print("🔑 Giriş yapılıyor...")
    USER = "43719"
    PASS = "RZpGH717"
    
    try:
        app = pywinauto.Application(backend="uia").connect(title_re=".*MatriksIQ Veri Terminali.*")
        win = app.top_window()
        print(f"Pencere: {win.texts()}")
        
        # Giriş bilgilerini yaz
        # Muhtemelen ilk alan kullanıcı adıdır. Değilse TAB ile ilerleyeceğiz.
        # win.type_keys(USER + "{TAB}" + PASS + "{ENTER}", with_spaces=True)
        # Bazen type_keys hızlı kaçar, karakter arası bekleme koyalım.
        win.type_keys(f"{USER}{'{TAB}'}{PASS}{'{ENTER}'}", pause=0.2)
        print("✅ Giriş bilgileri girildi ve ENTER basıldı.")
    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    login()
