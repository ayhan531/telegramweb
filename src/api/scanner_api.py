"""
Scanner API - Teknik Tarama ve Piyasa Analizi
Kaynak: TradingView (tvDatafeed)
"""
from tvDatafeed import TvDatafeed, Interval
import json
import sys
import random
from datetime import datetime

tv = TvDatafeed()

def safe_get_hist(symbol, exchange, interval, n_bars, retries=3):
    for i in range(retries):
        try:
            data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            if data is not None and not data.empty:
                return data
        except:
            pass
    return None

BIST30_SAMPLES = ['THYAO', 'SASA', 'EREGL', 'GARAN', 'ASELS', 'AKBNK', 'ISCTR', 'KCHOL', 'SISE', 'TUPRS']

def run_technical_scan():
    results = []
    for sym in BIST30_SAMPLES:
        try:
            hist = safe_get_hist(symbol=sym, exchange='BIST', interval=Interval.in_daily, n_bars=30)
            if hist is not None and len(hist) >= 20:
                price = hist['close'].iloc[-1]
                ma20 = hist['close'].rolling(window=20).mean().iloc[-1]
                
                # RSI Basit Hesaplama
                delta = hist['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1]))

                status = "NÖTR"
                if rsi > 70: status = "AŞIRI ALIM"
                elif rsi < 30: status = "AŞIRI SATIM"
                elif price > ma20: status = "GÜÇLÜ"
                
                results.append({
                    "symbol": sym,
                    "price": f"{price:.2f}",
                    "rsi": f"{rsi:.1f}",
                    "status": status,
                    "color": "#00ff88" if "GÜÇLÜ" in status or rsi < 30 else "#ff3b30" if rsi > 70 else "#60a5fa"
                })
        except: continue
    return results[:10]

def run_akd_scan():
    # BIST genelinde kurum aktivite simülasyonu
    kurumlar = ["İş Yatırım", "Garanti bbva", "Yapı Kredi", "BofA Securities", "QNB Finans"]
    results = []
    for k in kurumlar:
        net = random.randint(-500, 500)
        results.append({
            "kurum": k,
            "net_hacim": f"{abs(net)} M₺",
            "yon": "ALICI" if net > 0 else "SATICI",
            "color": "#00ff88" if net > 0 else "#ff3b30"
        })
    return results

def get_kap_news():
    news = [
        {"time": "09:15", "title": "BIST: Günlük bülten yayınlandı.", "source": "KAP", "urgent": False},
        {"time": "09:45", "title": "THYAO: Yeni uçak siparişi hakkında açıklama.", "source": "KAP", "urgent": True},
        {"time": "10:30", "title": "EREGL: Temettü ödeme takvimi kesinleşti.", "source": "Haber", "urgent": False},
        {"time": "11:20", "title": "Global Piyasalar: ABD enflasyon verisi bekleniyor.", "source": "Analiz", "urgent": False}
    ]
    return news

def get_scan_data(category):
    if category == 'teknik':
        return {"results": run_technical_scan()}
    elif category == 'akd':
        return {"results": run_akd_scan()}
    elif category == 'kap':
        return {"results": get_kap_news()}
    else:
        return {"error": "Geçersiz kategori"}

if __name__ == "__main__":
    cat = sys.argv[1] if len(sys.argv) > 1 else 'teknik'
    print(json.dumps(get_scan_data(cat), ensure_ascii=False))
