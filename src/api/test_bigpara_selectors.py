import requests
from bs4 import BeautifulSoup

def test_selectors():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = "https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/THYAO-detay/"
    
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    
    print("--- THYAO Hisse ---")
    price_tag = soup.select_one('.hisseProcessBar .value')
    change_tag = soup.select_one('.hisseProcessBar .item.percent span')
    print(f"Price: {price_tag.text if price_tag else 'None'}")
    print(f"Change: {change_tag.text if change_tag else 'None'}")
    
    print("\n--- Bitcoin ---")
    url_btc = "https://bigpara.hurriyet.com.tr/kripto-paralar/bitcoin-fiyati/"
    res_btc = requests.get(url_btc, headers=headers)
    soup_btc = BeautifulSoup(res_btc.text, 'lxml')
    values = soup_btc.select('.value')
    for v in values[:5]:
        print(f"BTC Value found: {v.text.strip()} | Parent: {v.parent.get('class')}")

if __name__ == "__main__":
    test_selectors()
