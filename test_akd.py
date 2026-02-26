import requests
import json
from datetime import datetime, timedelta

def test_isyatirim(symbol):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://www.isyatirim.com.tr/',
    }
    
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    print("Getting cookies...")
    session.get("https://www.isyatirim.com.tr/tr-tr/analiz/hisse/Sayfalar/default.aspx", headers=headers, timeout=10, verify=False)
    
    # 2. Call AKD API
    today = datetime.now().strftime("%d-%m-%Y")
    start_date = (datetime.now() - timedelta(days=5)).strftime("%d-%m-%Y")
    url = f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseAraciKurumDagilimi?hisse={symbol.upper()}&startdate={start_date}&enddate={today}"
    
    print(f"Calling API: {url}")
    headers.update({
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
    })
    
    resp = session.get(url, headers=headers, timeout=10, verify=False)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text[:500]}")
    
    try:
        data = resp.json()
        if data.get("ok"):
            print("SUCCESS! Found data.")
            return True
    except:
        pass
    return False

if __name__ == "__main__":
    test_isyatirim("THYAO")
