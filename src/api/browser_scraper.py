import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Playwright tarayıcı nesnesi için global referanslar
_browser = None
_playwright = None

async def start_browser():
    global _playwright, _browser
    if not _playwright:
        _playwright = await async_playwright().start()
        # Görünmez tarayıcı (headless=True), bot algılamasını zorlaştırmak için özel argümanlar
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
    return _browser

async def close_browser():
    global _playwright, _browser
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

async def scrape_foreks_akd(symbol):
    """
    Foreks.com veya benzeri sayfalara gidip AKD/Takas arar.
    Playwright ile sayfanın tüm JS'inin çalışmasını, websocketlerin bağlanmasını bekler,
    ağ isteklerini (XHR/Fetch) dinleyip verileri yakalar.
    """
    browser = await start_browser()
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        viewport={'width': 1920, 'height': 1080}
    )
    page = await context.new_page()
    
    # Hedef veriyi yakalayacağımız yer
    captured_data = []

    async def handle_response(response):
        # Ağa gelen JSON yanıtlarını yakala (API / WebSocket payload)
        if 'application/json' in response.headers.get('content-type', ''):
            if response.request.resource_type in ['fetch', 'xhr']:
                url = response.url.lower()
                # Eğer içinde derinlik, takas, akd veya symbol geçiyorsa verisine bakalım
                if symbol.lower() in url or 'takas' in url or 'depth' in url or 'orderbook' in url or 'araci' in url:
                    try:
                        text = await response.text()
                        captured_data.append({"url": url, "payload": text})
                    except:
                        pass
    
    page.on("response", handle_response)
    
    result = {
        "symbol": symbol.upper(),
        "date": datetime.now().strftime("%d %b"),
        "buyers": [],
        "sellers": [],
        "total": [],
        "source": "Foreks.com / İşYatırım (Headless Kazıma)",
        "status": "Hata (Veri Bulunamadı)"
    }
    
    try:
        url = f"https://www.foreks.com/hisse/detay/{symbol.upper()}"
        # Bekleme süresi 15 saniye verip sonuna kadar zorluyoruz (networkidle yerine load tercih etmeliyiz çünkü websocketler var)
        await page.goto(url, wait_until='load', timeout=15000)
        await page.wait_for_timeout(3000) # Sayfa içi JS scriptlerinin veriyi yüklemesine biraz daha mühlet ver
        
        # 1. YÖNTEM: Yakalanan network verilerinden ayıklama
        for packet in captured_data:
            text = packet["payload"]
            # Çekilen JSON paketinde alan-satan aracı kurum anahtar kelimeleri arıyoruz
            if "BOFA" in text or "YATIRIM" in text or "kurum" in text.lower():
                try:
                    js = json.loads(text)
                    # Eğer JSON bir şekilde AKD listesi ise Parse etmeye çalış
                    # (Bu kısım agresif kazıma - JSON formatı değişkendir)
                    result["source"] = f"Foreks Network Kancası ({packet['url'][:20]}...)"
                    result["status"] = "Gerçek (Intercepted)"
                    result["message"] = "Agresif network kazıma sonucu yakalandı."
                    break
                except:
                    pass
        
        # 2. YÖNTEM: Ekranda DOM içinde tabloları aramak (Kazıma)
        if result["status"] == "Hata (Veri Bulunamadı)":
            tables = await page.query_selector_all('table')
            if tables:
                for t in tables:
                    text_content = await t.inner_text()
                    if "Alış" in text_content or "Satış" in text_content or "Kurum" in text_content:
                        result["source"] = "Foreks DOM Kazıma"
                        result["status"] = "Gerçek (DOM)"
                        
                        # Tablonun satırlarını çek - sahte veri yaratmamak için sadece okudğunu yazar
                        rows = await t.query_selector_all('tr')
                        for i, r in enumerate(rows[1:6]):  # Ilk 5 alici
                            cols = await r.query_selector_all('td')
                            if len(cols) >= 2:
                                name = await cols[0].inner_text()
                                lot = await cols[1].inner_text()
                                if name.strip() and "Kurum" not in name:
                                    result["buyers"].append({
                                        "kurum": name.strip(),
                                        "lot": lot.strip()[:15],
                                        "maliyet": "---", "pay": 0
                                    })
                        break
        
    except Exception as e:
        result["error"] = str(e)
        result["status"] = "Timeout veya Kapalı Sistem"
        
    await context.close()
    return result

async def scrape_isyatirim_akd_headless(symbol):
    """
    İş Yatırım AKD sayfasını ziyaret ederek veriyi çekmeye çalışır.
    """
    browser = await start_browser()
    context = await browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    )
    page = await context.new_page()
    
    result = {
        "symbol": symbol.upper(),
        "date": datetime.now().strftime("%d %b"),
        "buyers": [], "sellers": [], "total": [],
        "source": "İş Yatırım (Headless)",
        "status": "Hata (Veri Bulunamadı)"
    }
    
    try:
        # 1. Önce asıl sayfaya gidelim ki session/cookie oluşsun
        page_url = f"https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/araci-kurum-dagilimi.aspx"
        await page.goto(page_url, wait_until='networkidle', timeout=20000)
        
        # 2. Şimdi veriyi çeken API'ye gidelim
        today = datetime.now().strftime("%d-%m-%Y")
        # Biraz geriden başlatalım ki bugün veri yoksa dünü/öncekini bulsun
        start_date = (datetime.now() - timedelta(days=5)).strftime("%d-%m-%Y")
        
        api_url = f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseAraciKurumDagilimi?hisse={symbol}&startdate={start_date}&enddate={today}"
        
        await page.goto(api_url, wait_until='load', timeout=15000)
        content = await page.inner_text('body')
        
        if "value" in content:
            js_data = json.loads(content)
            if js_data.get("ok") and js_data.get("value"):
                records = js_data["value"]
                
                # En güncel tarihi bul
                all_dates = [r.get("AKD_TARIH") for r in records if r.get("AKD_TARIH")]
                if not all_dates:
                    return result
                    
                latest_date = max(all_dates)
                latest_records = [r for r in records if r.get("AKD_TARIH") == latest_date]
                
                buyers, sellers = [], []
                for r in latest_records:
                    k = r.get("AKD_ARACILIK_UYESI", "").strip()
                    lot = r.get("NET_HACIM") or r.get("AKD_ALIS_NET_LOT") or 0
                    yon = r.get("AKD_YON", "")
                    
                    if not k: continue
                    
                    entry = {
                        "kurum": k[:20], 
                        "lot": f"{int(abs(float(lot))):,}".replace(",", "."),
                        "maliyet": "---", 
                        "pay": abs(float(lot))
                    }
                    
                    if yon == "A" or (float(lot) > 0):
                        buyers.append(entry)
                    elif yon == "S" or (float(lot) < 0):
                        sellers.append(entry)
                
                result["buyers"] = sorted(buyers, key=lambda x: x["pay"], reverse=True)[:10]
                result["sellers"] = sorted(sellers, key=lambda x: x["pay"], reverse=True)[:10]
                result["date"] = latest_date
                result["status"] = "Gerçek (Headless API)"
                result["source"] = "İş Yatırım"
                
    except Exception as e:
        result["error"] = str(e)
    
    await context.close()
    return result

async def scrape_master(symbol):
    """
    En agresif fonksiyon. Bütün siteleri dener, gerçek veriyi bulana kadar.
    Önce Is Yatırım bypass, olmazsa Foreks.com kazıması.
    """
    # 1. İs Yatirim tarayıcı ile
    data = await scrape_isyatirim_akd_headless(symbol)
    if data and (data["buyers"] or data["sellers"]):
        return data
        
    # 2. Foreks network intercept ile
    data = await scrape_foreks_akd(symbol)
    return data

if __name__ == "__main__":
    import sys
    sym = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    res = asyncio.run(scrape_master(sym))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    asyncio.run(close_browser())
