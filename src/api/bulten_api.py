import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import os
import json
import yfinance as yf
from datetime import datetime

def get_bulten_data():
    """
    BIST 100 özet verilerini ve yükselen/düşen hisseleri çeker.
    """
    try:
        # BIST 100 verisi (yfinance ile)
        symbol = "XU100.IS"
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        
        price = info['last_price']
        prev_close = info['previous_close']
        change_val = price - prev_close
        change_pct = (change_val / prev_close) * 100

        # Yükselenler / Düşürenler (Bloomberg HT üzerinden)
        url = "https://www.bloomberght.com/piyasalar"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        gainers = []
        losers = []
        
        # Bloomberg HT structure check
        # En çok artanlar/azalanlar widget'ları
        # Not: Bloomberg HT bazen dinamik yükler, alternatif olarak BigPara denenebilir.
        # Basitlik için bir diğer kaynak: 
        url_bigpara = "https://bigpara.hurriyet.com.tr/borsa/en-cok-artanlar/"
        res_bp = requests.get(url_bigpara, headers=headers)
        soup_bp = BeautifulSoup(res_bp.text, 'html.parser')
        
        # En çok artanlar
        rows = soup_bp.select(".clm2 ul li")
        for row in rows[:5]:
            cells = row.select("span")
            if len(cells) >= 3:
                gainers.append({
                    "symbol": cells[0].text.strip(),
                    "change": "+" + cells[2].text.strip()
                })
        
        # En çok azalanlar
        url_bp_losers = "https://bigpara.hurriyet.com.tr/borsa/en-cok-azalanlar/"
        res_bp_l = requests.get(url_bp_losers, headers=headers)
        soup_bp_l = BeautifulSoup(res_bp_l.text, 'html.parser')
        rows_l = soup_bp_l.select(".clm2 ul li")
        for row in rows_l[:5]:
            cells = row.select("span")
            if len(cells) >= 3:
                losers.append({
                    "symbol": cells[0].text.strip(),
                    "change": "-" + cells[2].text.strip()
                })

        day_names = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        now = datetime.now()
        date_str = f"{now.day} {['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'][now.month-1]} {day_names[now.weekday()]}"

        return {
            "index_name": "BIST 100",
            "price": f"{price:,.2f}".replace(',', '.'),
            "change": f"{change_pct:+.2f}%",
            "gainers": gainers,
            "losers": losers,
            "status": "POZİTİF" if change_pct >= 0 else "NEGATİF",
            "date": date_str
        }
    except Exception as e:
        # Hata durumunda boş değil, hata mesajı döner
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_bulten_data()
    print(json.dumps(res))
