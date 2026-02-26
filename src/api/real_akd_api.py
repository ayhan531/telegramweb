import os
import sys
import json
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import asyncio

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.isyatirim.com.tr/',
    'X-Requested-With': 'XMLHttpRequest',
}

# Create a global session to reuse cookies
session = requests.Session()
session.verify = False

def get_akd_from_isyatirim(symbol):
    """
    İş Yatırım üzerinden gerçek AKD (Aracı Kurum Dağılımı) verisini çeker.
    Bypass 401 by getting cookies first.
    """
    try:
        # 1. Warm up cookies if not already done
        if not session.cookies:
            session.get("https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx", headers=HEADERS, timeout=10)
            
        today = datetime.now().strftime("%d-%m-%Y")
        yesterday = (datetime.now() - timedelta(days=5)).strftime("%d-%m-%Y")
        
        url = (
            f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/"
            f"HisseAraciKurumDagilimi?hisse={symbol.upper()}&startdate={yesterday}&enddate={today}"
        )
        
        resp = session.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and data.get("value"):
                return parse_akd_isyatirim(data["value"], symbol)
        elif resp.status_code == 401:
            # Retry once with fresh cookies
            session.cookies.clear()
            session.get("https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx", headers=HEADERS, timeout=10)
            resp = session.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok") and data.get("value"):
                    return parse_akd_isyatirim(data["value"], symbol)
    except Exception as e:
        pass
    return None

def parse_akd_isyatirim(records, symbol):
    """
    İş Yatırım'dan gelen AKD JSON'ını alıcı/satıcı listesine dönüştürür.
    """
    buyers = []
    sellers = []
    
    # En güncel tarihi bul
    if not records:
        return None
    
    # Tarihe göre sırala, en son gün
    try:
        latest_date = max(r.get("AKD_TARIH", "") for r in records if r.get("AKD_TARIH"))
        latest = [r for r in records if r.get("AKD_TARIH") == latest_date]
    except:
        return None
    
    for r in latest:
        kurum = r.get("AKD_ARACILIK_UYESI", "").strip()
        lot = r.get("AKD_ALIS_NET_LOT") or r.get("NET_HACIM", 0)
        yon = r.get("AKD_YON", "")  # A=Alış, S=Satış
        
        if not kurum:
            continue
        
        entry = {
            "kurum": kurum[:20],
            "lot": f"{int(lot):,}".replace(",", ".") if lot else "0",
            "maliyet": "---",
            "pay": round(abs(float(lot or 0)) / 1_000_000, 2)
        }
        
        if yon == "A" or (lot and float(lot) > 0):
            buyers.append(entry)
        elif yon == "S" or (lot and float(lot) < 0):
            entry["lot"] = f"{int(abs(float(lot))):,}".replace(",", ".")
            sellers.append(entry)
    
    buyers = sorted(buyers, key=lambda x: x["pay"], reverse=True)[:10]
    sellers = sorted(sellers, key=lambda x: x["pay"], reverse=True)[:10]
    
    if not buyers and not sellers:
        return None
    
    return {
        "symbol": symbol.upper(),
        "date": latest_date,
        "buyers": buyers,
        "sellers": sellers,
        "total": [],
        "source": "İş Yatırım - Aracı Kurum Dağılımı (Güncel)",
        "status": "Gerçek Veri"
    }

def get_akd_from_bigpara_scrape(symbol):
    """
    Bigpara üzerinden AKD verisi scraping fallback.
    URL: https://bigpara.hurriyet.com.tr/hisse/THYAO/aracilar/ (Note: This URL often 404s now)
    """
    try:
        url = f"https://bigpara.hurriyet.com.tr/hisse/{symbol.upper()}/aracilar/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=8, verify=False)
        if resp.status_code != 200:
            return None
            
        soup = BeautifulSoup(resp.text, 'lxml')
        
        buyers = []
        sellers = []
        
        tables = soup.select('table.table')
        for idx, table in enumerate(tables[:2]):
            rows = table.select('tbody tr')
            for row in rows:
                cols = row.select('td')
                if len(cols) >= 2:
                    kurum = cols[0].get_text(strip=True)
                    lot_text = cols[1].get_text(strip=True).replace('.', '').replace(',', '.')
                    if kurum and kurum != "Kurum":
                        entry = {
                            "kurum": kurum[:20],
                            "lot": cols[1].get_text(strip=True),
                            "maliyet": "---",
                            "pay": 0.0
                        }
                        if idx == 0:
                            buyers.append(entry)
                        else:
                            sellers.append(entry)
        
        if buyers or sellers:
            return {
                "symbol": symbol.upper(),
                "date": datetime.now().strftime("%d %b"),
                "buyers": buyers[:10],
                "sellers": sellers[:10],
                "total": [],
                "source": "Bigpara - Aracı Kurum Dağılımı",
                "status": "Scraping"
            }
    except Exception:
        pass
    return None

async def get_real_akd_data(symbol):
    """
    Ana AKD fonksiyonu. Önce İş Yatırım API'sini dener, sonra Bigpara scraping.
    Eğer hepsi başarısız olursa, Playwright kullanan agressif Headless Scraper'a (browser_scraper.py) devredilir.
    """
    # 1. İş Yatırım API (en güvenilir) - Blocking calls run in thread
    try:
        print(f"DEBUG: Trying İş Yatırım API for {symbol}")
        data = await asyncio.to_thread(get_akd_from_isyatirim, symbol)
        if data and (data["buyers"] or data["sellers"]):
            return data
    except Exception as e:
        print(f"DEBUG: İş Yatırım API error: {e}")

    # 2. Bigpara scraping fallback
    try:
        print(f"DEBUG: Trying Bigpara Scrape for {symbol}")
        data = await asyncio.to_thread(get_akd_from_bigpara_scrape, symbol)
        if data and (data["buyers"] or data["sellers"]):
            return data
    except Exception as e:
        print(f"DEBUG: Bigpara Scrape error: {e}")
        
    # 3. Son çare: Agresif Başsız Tarayıcı Kazıması (Browser Scraper)
    try:
        print(f"DEBUG: Falling back to Headless Scraper for {symbol}...")
        from .browser_scraper import scrape_master
        headless_data = await scrape_master(symbol)
        if headless_data and (headless_data.get("buyers") or headless_data.get("status") != "Hata (Veri Bulunamadı)"):
            print(f"DEBUG: Headless Scraper SUCCESS for {symbol}")
            return headless_data
        else:
            print(f"DEBUG: Headless Scraper failed to find data for {symbol}")
    except Exception as e:
        print(f"DEBUG: Headless Scrape Exception: {e}")
        pass

    # 4. Hiçbiri çalışmazsa: Demo / Simüle Veri Gönder (Arayüz bozulmasın diye)
    print(f"DEBUG: Tümü başarısız. {symbol} için simüle edilmiş gösterim verisi oluşturuluyor.")
    return {
        "symbol": symbol.upper(),
        "date": datetime.now().strftime("%d %b %Y"),
        "buyers": [
            {"kurum": "Bank of America", "lot": "1.250.000", "pay": 35.5, "maliyet": "---"},
            {"kurum": "İş Yatırım", "lot": "850.000", "pay": 20.1, "maliyet": "---"},
            {"kurum": "Yapı Kredi", "lot": "420.000", "pay": 12.4, "maliyet": "---"},
            {"kurum": "Ziraat Yatırım", "lot": "310.000", "pay": 8.0, "maliyet": "---"},
            {"kurum": "Garanti BBVA", "lot": "150.000", "pay": 4.5, "maliyet": "---"}
        ],
        "sellers": [
            {"kurum": "Oyak Yatırım", "lot": "1.100.000", "pay": 32.0, "maliyet": "---"},
            {"kurum": "Tacirler Yatırım", "lot": "600.000", "pay": 18.2, "maliyet": "---"},
            {"kurum": "Gedik Yatırım", "lot": "450.000", "pay": 13.5, "maliyet": "---"},
            {"kurum": "Ak Yatırım", "lot": "280.000", "pay": 7.8, "maliyet": "---"},
            {"kurum": "Global Menkul", "lot": "120.000", "pay": 3.9, "maliyet": "---"}
        ],
        "total": [],
        "source": "SİMÜLASYON (Ücretsiz Kaynaklar Kapalı)",
        "status": "Demo Veri"
    }

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    import asyncio
    res = asyncio.run(get_real_akd_data(symbol))

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False, indent=2))
