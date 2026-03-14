import win32ui
import dde
import time

def test_dde():
    print("🛰️ DDE bağlantısı test ediliyor...")
    try:
        server = dde.CreateServer()
        server.Create("CheckDDE")
        
        conversation = dde.CreateConversation(server)
        
        # Matriks IQ DDE Servis ismi genelde 'MTX'
        try:
            conversation.ConnectTo("MTX", "QUOTE")
            print("✅ DDE Bağlantısı Başarılı!")
            
            # THYAO fiyatını çekmeyi dene
            # Not: Matriks IQ'da item formatı 'THYAO.SON' veya 'THYAO.LAST_PRICE' olabilir
            # Ayrıca 'SYMBOL.ALICI1', 'SYMBOL.SATICI1' vb.
            for item in ["THYAO.SON", "THYAO.LAST", "THYAO.CLOSE"]:
                try:
                    val = conversation.Request(item)
                    if val:
                        print(f"📈 {item}: {val}")
                        return True
                except: continue
                
        except Exception as e:
            print(f"❌ Matriks DDE Sunucusuna bağlanılamadı: {e}")
            print("💡 Matriks IQ'da DDE'nin açık olduğundan emin olun.")
            
    except Exception as e:
        print(f"Hata: {e}")
    return False

if __name__ == "__main__":
    test_dde()
