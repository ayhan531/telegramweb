import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_bigpara_data(symbol):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        price_tag = soup.select_one('.hisseProcessBar .value')
        change_tag = soup.select_one('.hisseProcessBar .item.percent span')
        name_tag = soup.select_one('.hisse-detay-header h1')
        
        stats = soup.select('.piyasaBox ul')
        low, high, open_val, volume = "0", "0", "0", "0"
        for s in stats:
            cap_tag = s.select_one('.cap')
            if not cap_tag: continue
            cap = cap_tag.text.strip().lower()
            val_tag = s.select_one('.area2') or s.select_one('.area1')
            if not val_tag: continue
            val = val_tag.text.strip()
            if 'düşük' in cap: low = val
            elif 'yüksek' in cap: high = val
            elif 'açılış' in cap: open_val = val
        
        vol_tag = soup.select_one('.hisseProcessBar li:nth-of-type(3) span b')
        if vol_tag: volume = vol_tag.text.strip()

        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            ch = 0.0
            if change_tag:
                try:
                    ch = float(change_tag.text.strip().replace('%', '').replace(',', '.'))
                except: pass
                
            return {
                "price": p,
                "change": ch,
                "name": name_tag.text.strip() if name_tag else symbol,
                "exchange": "BIST",
                "low": low,
                "high": high,
                "open": open_val,
                "volume": volume
            }
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Sembol bulunamadı (HTML parsing hatası)"}

def get_gram_gold():
    try:
        url = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        price_tag = soup.select_one('.detay-fiyat-top .item2 span:nth-of-type(2)')
        if not price_tag:
             price_tag = soup.select_one('.up .value') or soup.select_one('.dw .value')

        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            return {
                "price": p,
                "change": 0.0,
                "name": "Gram Altın",
                "exchange": "Foreks"
            }
    except:
        pass
    return {"error": "Altın verisi alınamadı"}

def get_tv_stock_data(symbol):
    """Alias for Telegram Bot compatibility"""
    data = get_bigpara_data(symbol)
    if "error" in data:
        return None
    # Adjusting format for main.py expectation
    return {
        "name": data.get("name", symbol),
        "price": data.get("price", 0.0),
        "currency": "TRY",
        "open": float(data.get("open", "0").replace(',', '.')),
        "high": float(data.get("high", "0").replace(',', '.')),
        "low": float(data.get("low", "0").replace(',', '.')),
        "volume": int(data.get("volume", "0").replace('.', '').replace(',', '') or 0)
    }

def get_tv_stock_history(symbol):
    """Simple history provider (returns last price as 1-day bar for now or uses yfinance)"""
    try:
        import yfinance as yf
        s = f"{symbol.upper()}.IS"
        data = yf.download(s, period="1mo", interval="1d", progress=False)
        return data
    except:
        return None

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    
    try:
        if symbol in ['GA', 'GRAMALTIN']:
            res = get_gram_gold()
        else:
            res = get_bigpara_data(symbol)
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
