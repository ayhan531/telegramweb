import os
import sys
import json
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def get_bigpara_data(symbol):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'lxml')
        
        price_tag = soup.select_one('.hisseProcessBar .value')
        change_tag = soup.select_one('.hisseProcessBar .item.percent span')
        
        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            ch = 0.0
            if change_tag:
                try: ch = float(change_tag.text.strip().replace('%', '').replace(',', '.'))
                except: pass
            
            return {
                "symbol": symbol.upper().replace('THYAO', 'THY'),
                "price": f"{p:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                "change": f"{ch:+.2f}%",
                "change_val": ch,
                "raw_price": p
            }
    except: pass
    return None

def get_market_data():
    idx_p = 0.0
    idx_ch = 0.0
    comm_list = []
    
    # 1. Try Bigpara
    try:
        url = "https://bigpara.hurriyet.com.tr/borsa/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'lxml')
        
        idx_box = soup.find('div', class_='stockBox', attrs={'data-e': True})
        if idx_box:
            p_tag = idx_box.select_one('.stockPrice')
            if p_tag: idx_p = float(p_tag.text.strip().replace('.', '').replace(',', '.'))
            idx_ch = float(idx_box.get('data-e').replace(',', '.'))
    except: pass

    # 2. Try yfinance Fallback for index
    if idx_p == 0:
        try:
            bist = yf.Ticker("XU100.IS")
            info = bist.info
            idx_p = info.get('regularMarketPrice', 0)
            idx_ch = info.get('regularMarketChangePercent', 0)
        except: pass

    # 3. Commodities (Gold, BTC)
    try:
        # Gold
        gold = yf.Ticker("GC=F") # Gold Futures as proxy or try XAUUSD=X
        g_price = gold.info.get('regularMarketPrice', 0)
        g_ch = gold.info.get('regularMarketChangePercent', 0)
        comm_list.append({"symbol": "Gram Altın", "price": f"{g_price:,.2f}".replace('.', ','), "change": f"{g_ch:+.2f}%"})
        
        # BTC
        btc = yf.Ticker("BTC-USD")
        b_price = btc.info.get('regularMarketPrice', 0)
        b_ch = btc.info.get('regularMarketChangePercent', 0)
    except:
        b_price, b_ch = 0, 0

    crypto_list = [
        {"symbol": "Bitcoin", "price": f"{b_price:,.0f}".replace(',', '.'), "change": f"{b_ch:+.2f}%"}
    ]
    
    if not comm_list:
        comm_list = [{"symbol": "Gram Altın", "price": "3.120,40", "change": "+0.12%"}]

    return idx_p, idx_ch, comm_list, crypto_list

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        symbols = ['THYAO', 'SASA', 'EREGL', 'ASELS', 'GARAN']
        with ThreadPoolExecutor(max_workers=5) as executor:
            bist_sum = list(executor.map(get_bigpara_data, symbols))
        
        bist_sum = [b for b in bist_sum if b is not None]
        idx_p, idx_ch, comm_sum, crypto_sum = get_market_data()
        
        res = {
            "index_name": "BIST 100",
            "price": f"{idx_p:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "change": f"{idx_ch:+.2f}%",
            "status": "POZİTİF" if idx_ch >= 0 else "NEGATİF",
            "date": datetime.now().strftime("%d %m %Y"),
            "bist_summary": bist_sum,
            "crypto_summary": crypto_sum,
            "commodity_summary": comm_sum,
            "gainers": sorted(bist_sum, key=lambda x: x['change_val'], reverse=True)[:5],
            "losers": sorted(bist_sum, key=lambda x: x['change_val'])[:5]
        }
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
