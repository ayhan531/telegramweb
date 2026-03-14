from pywinauto import Application, Desktop
import time
import os

def capture_matriks_data(symbol, command_key="{F2}", output_name="capture.png"):
    """
    Matriks IQ üzerinde sembol yazar ve ilgili fonksiyon tuşuyla (F2, F6 vb.) 
    açılan pencerenin görüntüsünü alır.
    """
    try:
        # 1. Ana pencereye bağlan
        app = Application(backend="uia").connect(title_re=".*MatriksIQ Veri Terminali.*")
        win = app.window(title_re=".*MatriksIQ Veri Terminali.*")
        win.set_focus()
        
        # 2. Sembol kutusunu bul ve yaz
        # Not: Önceki adımda 'Edit' tipindeki kutuları bulmuştuk
        found_box = False
        for c in win.descendants(control_type="Edit"):
            txt = c.window_text() or ""
            # Sembol kutusu genelde boş olur veya önceki sembolü içerir
            if len(txt) <= 10:
                try:
                    c.set_focus()
                    c.type_keys("^a{BACKSPACE}" + symbol + "{ENTER}")
                    found_box = True
                    break
                except: continue
        
        if not found_box:
            # Fallback: Direkt pencereye yaz (Bazı terminal ayarlarında direkt yazınca kutuya gider)
            win.type_keys(symbol + "{ENTER}")
            
        time.sleep(1)
        
        # 3. Komut tuşuna bas (F2=Derinlik, F6=AKD vb.)
        win.type_keys(command_key)
        print(f"Sent {command_key} for {symbol}...")
        time.sleep(2) # Pencerenin yüklenmesi için bekle
        
        # 4. Yeni açılan popup penceresini bul
        # Popup'lar genelde masaüstünde ayrı birer 'uia' penceresidir
        all_wins = Desktop(backend="uia").windows()
        target_win = None
        
        # Başlığa göre ara (Örn: 'THYAO - Derinlik' veya sadece 'THYAO')
        for w in all_wins:
            t = w.window_text() or ""
            if symbol in t and "Terminal" not in t:
                target_win = w
                break
        
        if target_win:
            print(f"🎯 Bulunan Pencere: {target_win.window_text()}")
            target_win.set_focus()
            img = target_win.capture_as_image()
            img.save(output_name)
            print(f"✅ Görüntü kaydedildi: {output_name}")
            # Opsiyonel: Pencereyi kapat ki ekran kalabalıklaşmasın
            # target_win.type_keys("%{F4}") 
            return True
        else:
            print(f"❌ {symbol} için popup penceresi bulunamadı.")
            # Yedek: Tüm ekranı çek (Nerede hata olduğunu görmek için)
            win.capture_as_image().save("error_state.png")
            return False
            
    except Exception as e:
        print(f"Hata: {e}")
        return False

if __name__ == "__main__":
    # Test: THYAO Derinlik (F2)
    capture_matriks_data("THYAO", "{F2}", "thyao_derinlik.png")
    # Test: THYAO AKD (F6)
    capture_matriks_data("THYAO", "{F6}", "thyao_akd.png")
