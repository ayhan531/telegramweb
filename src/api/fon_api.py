import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import os
import json

def get_fon_data():
    """
    Ekonomi portalları üzerinden popüler fon verilerini çeker.
    """
    try:
        url = "https://kur.doviz.com/fonlar"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        funds = []
        
        # doviz.com structure: table tbody tr
        rows = soup.select("table tbody tr")
        
        # Bot ekran görüntüsündeki gibi popüler fonları veya en çok artanları alalım
        for row in rows[:15]:
            cols = row.select("td")
            if len(cols) >= 3:
                code = cols[0].text.strip()
                name = cols[1].text.strip()
                change = cols[2].text.strip()
                
                # Sadece hisse senedi yoğun veya popüler olanları filtreleyebiliriz 
                # ama kullanıcı "gerçek veri" istediği için listedekileri veriyoruz.
                funds.append({
                    "code": code,
                    "name": name if len(name) < 25 else name[:22] + "...",
                    "change": ("+" if not change.startswith("-") else "") + change,
                    "color": "bg-blue-600", # Varsayılan renk
                    "icon": code[0]
                })

        if not funds:
             return {"error": "Veri kazınamadı"}
             
        return {"funds": funds}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_fon_data()
    print(json.dumps(res))
