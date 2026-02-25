import os
import sys
import json
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'tr-TR,tr;q=0.9',
    'Referer': 'https://www.isyatirim.com.tr/',
}

def get_takas_from_isyatirim(symbol):
    """
    İş Yatırım'dan MKK saklama/takas verisi çeker.
    Endpoint: HisseTakasDagilimi
    """
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        start = (datetime.now() - timedelta(days=7)).strftime("%d-%m-%Y")
        
        url = (
            f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/"
            f"HisseSaklamaDagilimi?hisse={symbol.upper()}&startdate={start}&enddate={today}"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and data.get("value"):
                return parse_takas_isyatirim(data["value"], symbol)
    except Exception:
        pass
    return None

def parse_takas_isyatirim(records, symbol):
    """
    İş Yatırım'dan gelen saklama verisini parse eder.
    """
    if not records:
        return None
    
    # En güncel tarihi bul
    latest_date = max(r.get("TARIH", "") for r in records if r.get("TARIH"))
    latest = [r for r in records if r.get("TARIH") == latest_date]
    
    holders = []
    total_lot = sum(float(r.get("SAKLAMA_LOT", 0) or 0) for r in latest)
    
    for r in latest:
        kurum = r.get("SAKLAMA_KURUMU") or r.get("KURUM_ADI") or r.get("kurum", "")
        lot = float(r.get("SAKLAMA_LOT") or r.get("LOT", 0) or 0)
        
        if not kurum or lot == 0:
            continue
        
        pay_pct = (lot / total_lot * 100) if total_lot > 0 else 0
        prev_lot = float(r.get("ONCEKI_LOT", lot) or lot)
        degisim = ((lot - prev_lot) / prev_lot * 100) if prev_lot > 0 else 0
        
        holders.append({
            "kurum": kurum[:25],
            "toplam_lot": f"{int(lot):,}".replace(",", "."),
            "pay": f"%{pay_pct:.2f}",
            "degisim": f"+{degisim:.1f}" if degisim >= 0 else f"{degisim:.1f}"
        })
    
    holders = sorted(holders, key=lambda x: float(x["pay"].replace("%", "").replace(",", ".")), reverse=True)
    
    if not holders:
        return None
    
    return {
        "symbol": symbol.upper(),
        "date": latest_date,
        "holders": holders[:10],
        "source": "İş Yatırım - MKK Saklama Dağılımı (Gerçek)",
        "status": "Güncel (EOD)"
    }

def get_takas_from_mkk_scrape(symbol):
    """
    MKK kamuya açık sayfasından saklama verisi scraping.
    """
    try:
        url = f"https://www.mkk.com.tr/tr/yatirimci-bilgileri/paydas-sayisi-belirleme"
        resp = requests.get(url, headers=HEADERS, timeout=8, verify=False)
        # MKK scraping için session ve form gerekiyor
        # Bu genellikle JS gerektiriyor, basit fallback
    except:
        pass
    return None

def get_takas_from_bigpara(symbol):
    """
    Bigpara'dan saklama/takas verisi scraping fallback.
    """
    try:
        url = f"https://bigpara.hurriyet.com.tr/hisse/{symbol.upper()}/sahiplik/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=8, verify=False)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        holders = []
        rows = soup.select('table tr') or soup.select('.takas-table tr')
        
        for row in rows[1:]:  # header skip
            cols = row.select('td')
            if len(cols) >= 3:
                kurum = cols[0].get_text(strip=True)
                lot = cols[1].get_text(strip=True)
                pay = cols[2].get_text(strip=True)
                if kurum and kurum != "Kurum":
                    holders.append({
                        "kurum": kurum[:25],
                        "toplam_lot": lot,
                        "pay": pay,
                        "degisim": "---"
                    })
        
        if holders:
            return {
                "symbol": symbol.upper(),
                "date": datetime.now().strftime("%d/%m/%Y"),
                "holders": holders[:10],
                "source": "Bigpara - Saklama Dağılımı",
                "status": "Güncel"
            }
    except:
        pass
    return None

def get_takas_data(symbol):
    """
    Ana takas fonksiyonu.
    1. İş Yatırım MKK saklama API
    2. Bigpara scraping
    """
    # 1. İş Yatırım
    data = get_takas_from_isyatirim(symbol)
    if data and data.get("holders"):
        return data
    
    # 2. Bigpara scraping
    data = get_takas_from_bigpara(symbol)
    if data and data.get("holders"):
        return data
    
    # 3. Hata durumu
    return {
        "symbol": symbol.upper(),
        "date": datetime.now().strftime("%d/%m/%Y"),
        "holders": [],
        "source": "Veri Alınamadı",
        "status": "Hata"
    }


if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    res = get_takas_data(symbol)

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False, indent=2))
