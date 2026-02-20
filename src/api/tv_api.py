from tvDatafeed import TvDatafeed, Interval
import os
from dotenv import load_dotenv
# Load environment variables from root
current_dir = os.path.dirname(os.path.abspath(__file__)) # src/api
root_dir = os.path.dirname(os.path.dirname(current_dir)) # root
load_dotenv(os.path.join(root_dir, '.env'))

# TradingView bağlantısını başlat
username = os.getenv("TV_USERNAME")
password = os.getenv("TV_PASSWORD")

tv = TvDatafeed(username, password)

def get_tv_stock_data(symbol: str):
    try:
        data = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_1_minute, n_bars=1)
        if data is None or data.empty:
            return None
        latest = data.iloc[-1]
        return {
            "price": latest['close'],
            "open": latest['open'],
            "high": latest['high'],
            "low": latest['low'],
            "volume": latest['volume'],
            "change": 0.0,
            "name": symbol,
            "currency": "TRY"
        }
    except Exception as e:
        print(f"TradingView Hatası: {e}")
        return None

def get_tv_akd_data(symbol: str):
    try:
        data = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_1_minute, n_bars=100)
        if data is None or data.empty:
            return None
        buy_vol = data[data['close'] > data['open']]['volume'].sum()
        sell_vol = data[data['close'] < data['open']]['volume'].sum()
        total_vol = data['volume'].sum()
        net_vol = buy_vol - sell_vol
        return {
            "net_volume": net_vol,
            "buy_ratio": (buy_vol / total_vol) * 100 if total_vol > 0 else 0,
            "sell_ratio": (sell_vol / total_vol) * 100 if total_vol > 0 else 0,
            "total_volume": total_vol
        }
    except Exception as e:
        print(f"AKD Simülasyon Hatası: {e}")
        return None

def get_tv_stock_history(symbol: str, n_bars=100):
    try:
        data = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=n_bars)
        return data
    except Exception as e:
        print(f"TradingView Hatası: {e}")
        return None

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        sym = sys.argv[1].upper()
        res = get_tv_stock_data(sym)
        if res:
            for k, v in res.items():
                if isinstance(v, float) and (v != v):
                    res[k] = None
            print(json.dumps(res))
        else:
            print(json.dumps({"error": "Veri bulunamadı"}))
