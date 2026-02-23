"""
Takas Veri API (Simüle)
Kaynak: TradingView (tvDatafeed)
"""
from tvDatafeed import TvDatafeed, Interval
import json
import sys
import random
from datetime import datetime

tv = TvDatafeed()

def safe_get_hist(symbol, exchange, interval, n_bars, retries=3):
    """Bağlantı hatalarına karşı güvenli veri çekme."""
    for i in range(retries):
        try:
            data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            if data is not None and not data.empty:
                return data
        except:
            pass
    return None

SAKLAMA_KURUMLARI = [
    "Merkezi Kayıt Kuruluşu", "Euroclear Bank", "Clearstream",
    "İş Yatırım Saklama", "Garanti Yatırım Saklama", "Yapı Kredi Saklama"
]

def get_takas_data(symbol: str):
    try:
        symbol = symbol.upper()
        if any(c in symbol for c in ['USDT', 'ETH', 'BTC']):
             return {"error": "Takas Analizi sadece BIST içindir."}
             
        # Günlük hacim
        hist = safe_get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=1)
        if hist is None or hist.empty: return None
            
        total_lot = int(hist['volume'].iloc[-1])
        price = float(hist['close'].iloc[-1])

        random.seed(hash(symbol) + 123)
        weights = sorted([random.random() for _ in range(6)], reverse=True)
        sum_w = sum(weights)

        holders = []
        for i, kurum in enumerate(SAKLAMA_KURUMLARI):
            lot = int(total_lot * (weights[i]/sum_w)) if total_lot > 0 else 0
            pay = round((weights[i]/sum_w) * 100, 2)
            holders.append({
                "kurum": kurum,
                "toplam_lot": f"{lot:,}",
                "pay": f"%{pay:.2f}"
            })

        return {
            "symbol": symbol,
            "total_volume": total_lot,
            "price": round(price, 2),
            "holders": holders
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(get_takas_data(sys.argv[1]), ensure_ascii=False))
