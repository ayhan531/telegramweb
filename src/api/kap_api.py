import os
import sys
import json
import requests
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html, */*',
    'Accept-Language': 'tr-TR,tr;q=0.9',
}

def get_kap_from_rss():
    """
    KAP RSS feed'inden gerçek bildirimleri çeker.
    """
    try:
        url = "https://www.kap.org.tr/rss/bildirim.aspx"
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        
        if resp.status_code != 200:
            return None
        
        root = ET.fromstring(resp.content)
        channel = root.find('channel')
        if not channel:
            return None
        
        items = []
        for item in channel.findall('item')[:20]:
            title = item.findtext('title', '').strip()
            pub_date = item.findtext('pubDate', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            
            # Saat bilgisini çıkar
            time_str = "---"
            if pub_date:
                try:
                    from email.utils import parsedate
                    parsed = parsedate(pub_date)
                    if parsed:
                        dt = datetime(*parsed[:6])
                        time_str = dt.strftime("%H:%M")
                except:
                    pass
            
            # Başlıktan şirket adını ve kategoriyi çıkar
            parts = title.split(" - ") if " - " in title else [title]
            company = parts[0].strip() if parts else "KAP"
            content = parts[-1].strip() if len(parts) > 1 else title
            
            # Urgency: finansal tablo, sözleşme, temettü gibi önemli başlıklar
            urgent_keywords = ["temettü", "sözleşme", "ihale", "finansal tablo", "özel durum", "pay alım"]
            urgent = any(kw in content.lower() for kw in urgent_keywords)
            
            items.append({
                "source": company,
                "time": time_str,
                "title": content[:120],
                "link": link,
                "urgent": urgent
            })
        
        return items if items else None
    
    except Exception as e:
        return None

def get_kap_from_scraping():
    """
    KAP bildirim sayfasını scraping ile çeker.
    """
    try:
        url = "https://www.kap.org.tr/tr/bildirim-sorgu"
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        items = []
        rows = soup.select('.w-clearfix.w-inline-block.comp-row') or \
               soup.select('div[class*="bildirim"]') or \
               soup.select('ul.disclosure-list li')
        
        for row in rows[:15]:
            text = row.get_text(separator=' ', strip=True)
            if text and len(text) > 10:
                items.append({
                    "source": "KAP",
                    "time": datetime.now().strftime("%H:%M"),
                    "title": text[:120],
                    "link": "",
                    "urgent": False
                })
        
        return items if items else None
    except:
        return None

def get_kap_from_isyatirim():
    """
    İş Yatırım üzerinden haberleri çeker (fallback).
    Son 7 günü kontrol eder.
    """
    try:
        today = datetime.now()
        bitis = today.strftime("%d-%m-%Y")
        baslangic = (today - timedelta(days=7)).strftime("%d-%m-%Y")
        
        url = f"https://www.isyatirim.com.tr/_layouts/15/Isyatirim.Website/Common/Data.aspx/HisseHaberler?baslangic={baslangic}&bitis={bitis}"
        
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok") and data.get("value"):
                items = []
                for r in data["value"][:20]:
                    baslik = r.get("haberBasligi") or r.get("title") or r.get("HABER_BASLIK", "")
                    hisse = r.get("hisseKodu") or r.get("HISSE_KODU", "KAP")
                    tarih = r.get("haberTarihi") or r.get("TARIH", "")
                    
                    # Saat çıkar
                    time_str = "---"
                    if tarih:
                        try:
                            # 2026-03-02T08:30:00 or similar
                            if "T" in str(tarih):
                                dt = datetime.fromisoformat(str(tarih).replace("Z", ""))
                                day_str = dt.strftime("%d.%m")
                                time_str = f"{day_str} {dt.strftime('%H:%M')}"
                            else:
                                time_str = str(tarih)[:10]
                        except:
                            pass
                    
                    if baslik:
                        urgent_keywords = ["temettü", "sözleşme", "finansal", "ihale", "pay alım"]
                        urgent = any(kw in baslik.lower() for kw in urgent_keywords)
                        items.append({
                            "source": hisse,
                            "time": time_str,
                            "title": baslik[:120],
                            "link": "",
                            "urgent": urgent
                        })
                return items if items else None
    except Exception as e:
        sys.stderr.write(f"Isyatirim KAP Error: {str(e)}\n")
    return None

def get_kap_from_bigpara():
    """
    Bigpara KAP haberleri sayfasını küçültür.
    """
    try:
        url = "https://bigpara.hurriyet.com.tr/borsa/kap-haberleri/"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        items = []
        # Bigpara haber listesi genellikle 'div.news-list-item' veya benzeri
        rows = soup.select('.kap-list-item') or soup.find_all('div', class_='news-list')
        
        for row in rows[:15]:
            text = row.get_text(separator=' ', strip=True)
            # Genellikle "Şirket Adı - Başlık" formatında olur
            if text and len(text) > 15:
                # Zaman formatını ayıkla (genellikle en başta "15:45" gibi)
                time_str = "---"
                import re
                time_match = re.search(r'(\d{2}:\d{2})', text)
                if time_match:
                    time_str = time_match.group(1)
                
                items.append({
                    "source": "KAP",
                    "time": time_str,
                    "title": text[:120],
                    "link": "",
                    "urgent": any(k in text.lower() for k in ["temettü", "sözleşme", "ihale"])
                })
        
        return items if items else None
    except:
        return None

def get_kap_ajan(symbol=None):
    """
    Ana KAP fonksiyonu. Önce RSS, sonra isyatirim, sonra bigpara, sonra scraping.
    """
    # 1. KAP RSS (en güncel)
    items = get_kap_from_rss()
    if not items:
        # 2. İş Yatırım haberleri as primary fallback
        items = get_kap_from_isyatirim()
    if not items:
        # 3. Bigpara
        items = get_kap_from_bigpara()
    
    if items:
        if symbol:
            s_up = symbol.upper()
            filtered = [i for i in items if s_up in i.get("source", "").upper() or s_up in i.get("title", "").upper()]
            if filtered: return filtered
            return [{
                "source": s_up, 
                "time": datetime.now().strftime("%H:%M"), 
                "title": f"'{s_up}' ile ilgili son 24 saatte yeni bildirim bulunamadı.", 
                "urgent": False
            }]
        return items
    
    # Final Backup (Boş kalmasın)
    return [
        {"source": "SİSTEM", "time": datetime.now().strftime("%H:%M"), "title": "Piyasa akışı aktif. Yeni bildirimler için beklemede kalın.", "urgent": False}
    ]


if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else None
    res = {"results": get_kap_ajan(symbol)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
