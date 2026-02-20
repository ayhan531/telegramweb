import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load environment variables from root
current_dir = os.path.dirname(os.path.abspath(__file__)) # src/api
root_dir = os.path.dirname(os.path.dirname(current_dir)) # root
load_dotenv(os.path.join(root_dir, '.env'))
import sys

def get_takas_data(symbol: str):
    """
    İş Yatırım üzerinden Takas (Settlement) verilerini çeker.
    """
    try:
        url = f"https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/takas-degisimi.aspx?hisse={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Takas tablosunu bul (Genelde ilk tablo veya id/class ile aranabilir)
        # İş Yatırım'da takas tablosu genellikle id="takasTablo" gibi bir yapıdadır
        table = soup.find('table', {'id': 'takasTablo'}) or soup.find('table')
        
        if not table:
            return None
            
        holders = []
        rows = table.find_all('tr')
        
        for row in rows[1:]: # Başlığı geç
            cols = row.find_all('td')
            if len(cols) >= 3:
                holders.append({
                    "kurum": cols[0].text.strip(),
                    "toplam_lot": cols[1].text.strip(),
                    "pay": cols[2].text.strip()
                })
        
        return {
            "symbol": symbol,
            "holders": holders[:20] # İlk 20 kurumu döndür
        }
    except Exception as e:
        print(f"Takas Hatası: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sym = sys.argv[1].upper()
        res = get_takas_data(sym)
        if res:
            print(json.dumps(res))
        else:
            print(json.dumps({"error": "Veri bulunamadı"}))
