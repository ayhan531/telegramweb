import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from bs4 import BeautifulSoup
import os
import json
from dotenv import load_dotenv

# Load environment variables from root
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
load_dotenv(os.path.join(root_dir, '.env'))

def get_fon_data():
    """
    TEFAS veya İş Yatırım üzerinden popüler fon verilerini çeker.
    """
    try:
        # Örnek olarak popüler fonları içeren bir tabloyu veya mock veriyi çekelim
        # Gerçek kazıma için TEFAS'ın API'si veya post istekleri gerekebilir. 
        # Botun ekran görüntüsünde Sabit fonlar (KHA, GAF, AHI, RHS, GMR) vardı.
        
        funds = [
            {"code": "KHA", "name": "PARDUS PORTFÖY İKİN...", "change": "+10,33%", "color": "bg-indigo-600", "icon": "P"},
            {"code": "GAF", "name": "INVEO PORTFÖY BİRİN...", "change": "+9,78%", "color": "bg-blue-600", "icon": "INVEO"},
            {"code": "AHI", "name": "ATLAS PORTFÖY BİRİN...", "change": "+7,97%", "color": "bg-cyan-600", "icon": "A"},
            {"code": "RHS", "name": "ROTA PORTFÖY HİSSE ...", "change": "+7,40%", "color": "bg-purple-600", "icon": "*"},
            {"code": "GMR", "name": "INVEO PORTFÖY İKİNC...", "change": "+2,17%", "color": "bg-blue-600", "icon": "INVEO"}
        ]
        
        # Gelecekte buraya gerçek TEFAS kazıyıcısı eklenebilir.
        return {"funds": funds}
    except Exception as e:
        print(f"Fon Hatası: {e}")
        return None

if __name__ == "__main__":
    res = get_fon_data()
    if res:
        print(json.dumps(res))
    else:
        print(json.dumps({"error": "Fon verisi alınamadı"}))
