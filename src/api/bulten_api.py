import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def get_live_price_bigpara(symbol_type, symbol):
    """
    symbol_type: 'hisse', 'doviz', 'altin', 'kripto'
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        if symbol_type == 'hisse':
            url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        elif symbol_type == 'doviz':
            url = f"https://bigpara.hurriyet.com.tr/doviz/{symbol.lower()}/"
        elif symbol_type == 'altin':
            url = f"https://bigpara.hurriyet.com.tr/altin/{symbol.lower()}-fiyati/"
        elif symbol_type == 'kripto':
            url = f"https://bigpara.hurriyet.com.tr/kripto-paralar/{symbol.lower()}-fiyati/"
        else:
            return None

        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        # Bigpara has different structures for different pages
        if symbol_type == 'hisse':
            price_tag = soup.select_one('.hisseProcessBar .value')
            change_tag = soup.select_one('.hisseProcessBar .item.percent span')
        else:
            # For gold, currency, crypto
            price_tag = soup.select_one('.kurBox .value') or soup.select_one('.data.m7 .value') or soup.select_one('.m7 .value')
            change_tag = soup.select_one('.kurBox .percent .value') or soup.select_one('.data.m7 .percent .value') or soup.select_one('.m7 .percent .value')

        if price_tag:
            price_str = price_tag.text.strip().replace('.', '').replace(',', '.')
            price_val = float(price_str)
            
            change_val = 0.0
            if change_tag:
                try:
                    change_val = float(change_tag.text.strip().replace('%', '').replace(',', '.'))
                except: pass
            
            return {
                "symbol": symbol.upper(),
                "price": f"{price_val:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                "change": f"{change_val:+.2f}%",
                "change_val": change_val,
                "raw_price": price_val
            }
    except Exception as e:
        # sys.stderr.write(f"Error fetching {symbol}: {e}\n")
        pass
    return None

def get_bist_index():
    try:
        url = "https://bigpara.hurriyet.com.tr/borsa/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        idx_box = soup.find('div', class_='stockBox', attrs={'data-e': True})
        if idx_box:
            p_tag = idx_box.select_one('.stockPrice')
            p = float(p_tag.text.strip().replace('.', '').replace(',', '.'))
            ch = float(idx_box.get('data-e').replace(',', '.'))
            return p, ch
    except: pass
    return 0.0, 0.0

def get_bulten_data():
    idx_p, idx_ch = get_bist_index()
    
    # Popular symbols for gainers/losers
    popular_symbols = [
        'THYAO', 'SASA', 'EREGL', 'ASELS', 'GARAN', 'AKBNK', 'ISCTR', 'YKBNK', 'KCHOL', 'SAHOL', 
        'TUPRS', 'SISE', 'BIMAS', 'HEKTS', 'KOZAL', 'PETKM', 'PGSUS', 'TOASO', 'ARCLK', 'FROTO'
    ]
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        bist_results = list(executor.map(lambda s: get_live_price_bigpara('hisse', s), popular_symbols))
    
    bist_sum = [b for b in bist_results if b is not None]
    
    # Market Stats
    usd = get_live_price_bigpara('doviz', 'dolar')
    gold = get_live_price_bigpara('altin', 'gram-altin')
    btc = get_live_price_bigpara('kripto', 'bitcoin')
    
    # Fallbacks if scraping fails (more realistic than hardcoded old values)
    if not usd: usd = {"symbol": "DOLAR", "price": "GÜNCELLENİYOR", "change": "%0.00"}
    if not gold: gold = {"symbol": "GRAM ALTIN", "price": "GÜNCELLENİYOR", "change": "%0.00"}
    if not btc: btc = {"symbol": "BITCOIN", "price": "GÜNCELLENİYOR", "change": "%0.00"}

    valid_bist = [b for b in bist_sum if b and isinstance(b.get('change_val'), (int, float))]

    return {
        "index_name": "BIST 100",
        "price": f"{idx_p:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
        "change": f"{idx_ch:+.2f}%",
        "status": "POZİTİF" if idx_ch >= 0 else "NEGATİF",
        "date": datetime.now().strftime("%d %m %Y"),
        "bist_summary": bist_sum,
        "crypto_summary": [btc],
        "commodity_summary": [gold, usd],
        "gainers": sorted([b for b in valid_bist if b['change_val'] > 0], key=lambda x: x['change_val'], reverse=True)[:5],
        "losers": sorted([b for b in valid_bist if b['change_val'] < 0], key=lambda x: x['change_val'])[:5]
    }

if __name__ == "__main__":
    # Suppress output from libraries
    _orig_stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    
    try:
        res = get_bulten_data()
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    print(json.dumps(res, ensure_ascii=False))
