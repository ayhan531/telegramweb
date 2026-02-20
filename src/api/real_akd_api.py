import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_real_akd_data(symbol: str):
    """
    İş Yatırım üzerinden gerçek Aracı Kurum Dağılımı (AKD) verilerini çeker.
    """
    try:
        url = f"https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/araci-kurum-dagilimi.aspx?hisse={symbol}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        if not tables:
            return None
            
        buyers = []
        sellers = []
        
        # Alıcılar tablosu - Sınırlandırılmamış tüm satırlar
        for row in tables[0].find_all('tr')[1:]: 
            cols = row.find_all('td')
            if len(cols) >= 2:
                buyers.append({
                    "kurum": cols[0].text.strip(), 
                    "lot": cols[1].text.strip(), 
                    "pay": cols[2].text.strip() if len(cols) > 2 else "0"
                })
                
        # Satıcılar tablosu - Sınırlandırılmamış tüm satırlar
        if len(tables) > 1:
            for row in tables[1].find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    sellers.append({
                        "kurum": cols[0].text.strip(), 
                        "lot": cols[1].text.strip(), 
                        "pay": cols[2].text.strip() if len(cols) > 2 else "0"
                    })

        return {
            "symbol": symbol,
            "buyers": buyers,
            "sellers": sellers
        }
    except Exception as e:
        print(f"Gerçek AKD Hatası: {e}")
        return None
