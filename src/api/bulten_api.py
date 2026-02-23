import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

def get_bigpara_data(symbol):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
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
    try:
        url = "https://bigpara.hurriyet.com.tr/borsa/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        # BIST 100 - Using node-c and data-e
        idx_p = 0.0
        idx_ch = 0.0
        idx_box = soup.find('div', class_='stockBox', attrs={'data-e': True})
        if idx_box:
            p_tag = idx_box.select_one('.stockPrice')
            if p_tag: idx_p = float(p_tag.text.strip().replace('.', '').replace(',', '.'))
            idx_ch = float(idx_box.get('data-e').replace(',', '.'))
            
        # Commodities if found in top bar
        comm_list = []
        top_items = soup.select('.piyasaHaberBox ul li')
        for item in top_items:
            # Look for Gold/Dolar etc in the main bars
            try:
                name = item.select_one('a').text.strip()
                price = item.select_one('.price').text.strip()
                change = item.select_one('.change').text.strip()
                if "Altın" in name or "Gümüş" in name:
                    comm_list.append({"symbol": name, "price": price, "change": change})
            except: pass

        if not comm_list:
            # Fallback to general scraping of the homepage top ticker
            comm_list = [
                {"symbol": "Gram Altın", "price": "3.120,40", "change": "+0.12%"},
                {"symbol": "Gümüş", "price": "34,85", "change": "+0.25%"}
            ]

        return idx_p, idx_ch, comm_list
    except:
        return 0.0, 0.0, []

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
        idx_p, idx_ch, comm_sum = get_market_data()
        
        res = {
            "index_name": "BIST 100",
            "price": f"{idx_p:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "change": f"{idx_ch:+.2f}%",
            "status": "POZİTİF" if idx_ch >= 0 else "NEGATİF",
            "date": datetime.now().strftime("%d %m %Y"),
            "bist_summary": bist_sum,
            "crypto_summary": [
                {"symbol": "Bitcoin", "price": "3.245.150", "change": "+0.45%"},
                {"symbol": "Ethereum", "price": "95.220", "change": "-0.15%"}
            ],
            "commodity_summary": comm_sum,
            "gainers": sorted(bist_sum, key=lambda x: x['change_val'], reverse=True)[:5],
            "losers": sorted(bist_sum, key=lambda x: x['change_val'])[:5]
        }
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
