# Matriks <-> Telegram Bot Veri Köprüsü

Bu script, kendi bilgisayarında açık olan **Matriks Terminal (Masaüstü)** uygulamasından canlı **Aracı Kurum Dağılımı (AKD)** verilerini alabilmeni ve arka planda, sessizce, Render üzerinde çalışan Telegram botuna iletmeni sağlar.

## Kurulum (Kendi Windows Bilgisayarın İçin)

1. Python yüklü değilse `python.org` sitesinden indirip yükle. (Yüklerken alt kısımdaki "Add Python to PATH" seçeneğini MÜHAKKAK işaretle).
2. Terminal (Komut İstemi - Cmd) aç ve şu kütüphaneleri yükle:
   ```cmd
   pip install requests pyperclip
   ```
3. `run_bridge.py` içindeki `API_TOKEN` değerini, senin botuna erişimi olan şifren olarak bırak (Biz `.env` dosyannda da `MATRIKS_BRIDGE_TOKEN=MATRIKS_GIZLI_TOKEN_123` ekleyeceğiz).
4. `run_bridge.py` dosyasını çalıştır. Siyah bir pencere arka planda bekleyecek.

## Nasıl Kullanılır?

- Gün içinde bir hissenin AKD'sine bakmak veya botu kullananlara iletmek mi istiyorsun?
- Matriks'ten ilgili hissenin AKD tablosunu aç.
- Hepsini seç ve **Kopyala** (Ctrl+C veya Sağ Tık -> Kopyala).
- Arka planda bekleyen bizim küçük siyah `run_bridge` programımız hemen yeni bir AKD verisi kopyaladığını algılayacak.
- "Hangi hisseyi kopyaladın?" diye soracak, `THYAO` yazıp **Enter**'a bas.
- Anında o veri 7/24 uyanık olan Render sunucusuna (`api_server.js`) POST atılarak kaydedilecek. Telegramdaki kullanıcı `/akd THYAO` yazdığı anda, doğrudan senin 2 saniye önce kopyaladığın **100% Gerçek** verileri görecek :)

Bu yöntem, İş Yatırım ve Foreks gibi tüm sitelerin ücretsiz kazımayı kapattığı yeni düzende yapabileceğin en pürüzsüz "manuel-canlı" entegrasyondur. İleride Excel DDE (Canlı Aktarım) özelliğine de geliştirilebiliriz.
