import os
import sys
import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

def get_fon_data(code):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{code.upper()}-detay/" # Fonlar da benzer url yapısına sahip olabiliyor veya TEFAS
        # TEFAS genelde tercih edilir ama Bigpara üzerinden de deniyoruz
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        
        price_tag = soup.select_one('.hisseProcessBar .value')
        change_tag = soup.select_one('.hisseProcessBar .item.percent span')
        
        if price_tag:
            p = float(price_tag.text.strip().replace('.', '').replace(',', '.'))
            ch = float(change_tag.text.strip().replace('%', '').replace(',', '.')) if change_tag else 0.0
            return {
                "code": code.upper(),
                "name": code.upper(),
                "change": f"{ch:+.2f}%",
                "color": "bg-yellow-600" if "GOLD" in code.upper() else "bg-blue-600",
                "icon": code[0]
            }
    except: pass
    return None

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        etf_list = ['GLDTR', 'USDTR', 'GUMUS', 'ZRE20', 'KCHOL']
        with ThreadPoolExecutor(max_workers=5) as executor:
            funds = list(executor.map(get_fon_data, etf_list))
        
        funds = [f for f in funds if f is not None]
        res = {"funds": funds}
    except Exception as e:
        res = {"error": str(e), "funds": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
