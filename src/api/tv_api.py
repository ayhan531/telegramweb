import os
import sys
import json
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

def get_bigpara_data(symbol):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'lxml')
        
        price_tag = soup.select_one('.hisseProcessBar .value')
        change_tag = soup.select_one('.hisseProcessBar .item.percent span')
        name_tag = soup.select_one('.hisse-detay-header h1')
        
        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            ch = 0.0
            if change_tag:
                try: ch = float(change_tag.text.strip().replace('%', '').replace(',', '.'))
                except: pass
            
            # Stats extraction
            stats = soup.select('.piyasaBox ul')
            low, high, open_val = "0", "0", "0"
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
            volume = vol_tag.text.strip() if vol_tag else "0"

            return {
                "price": p,
                "change": ch,
                "name": name_tag.text.strip() if name_tag else symbol,
                "exchange": "BIST",
                "low": low,
                "high": high,
                "open": open_val,
                "volume": volume,
                "source": "Bigpara"
            }
    except: pass
    return None

def get_yfinance_fallback(symbol):
    try:
        s = f"{symbol.upper()}.IS"
        ticker = yf.Ticker(s)
        info = ticker.info
        if info and 'regularMarketPrice' in info:
            return {
                "price": info.get('regularMarketPrice'),
                "change": info.get('regularMarketChangePercent', 0.0),
                "name": info.get('longName', symbol),
                "exchange": "BIST",
                "low": str(info.get('dayLow', 0)),
                "high": str(info.get('dayHigh', 0)),
                "open": str(info.get('regularMarketOpen', 0)),
                "volume": str(info.get('volume', 0)),
                "source": "yfinance (Fallback)"
            }
    except: pass
    return None

def get_history_data(symbol):
    try:
        s = f"{symbol.upper()}.IS"
        df = yf.download(s, period="1mo", interval="1d", progress=False)
        if df.empty: return []
        
        history = []
        for index, row in df.iterrows():
            history.append({
                "date": index.strftime('%Y-%m-%d'),
                "price": float(row['Close'])
            })
        return history
    except: return []

def get_unified_data(symbol):
    data = get_bigpara_data(symbol)
    if data: return data
    data = get_yfinance_fallback(symbol)
    if data: return data
    return {"error": "Sembol bulunamadı"}

def get_gram_gold():
    try:
        url = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'lxml')
        price_tag = soup.select_one('.detay-fiyat-top .item2 span:nth-of-type(2)') or \
                    soup.select_one('.up .value') or soup.select_one('.dw .value')
        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            return {"price": p, "change": 0.0, "name": "Gram Altın", "exchange": "Foreks", "source": "Bigpara"}
    except: pass
    return {"error": "Altın verisi alınamadı"}

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    mode = sys.argv[2] if len(sys.argv) > 2 else 'data'
    
    if mode == 'history':
        res = get_history_data(symbol)
    elif symbol in ['GA', 'GRAMALTIN']:
        res = get_gram_gold()
    else:
        res = get_unified_data(symbol)

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
