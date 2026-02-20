from tvDatafeed import TvDatafeed, Interval
import os
from dotenv import load_dotenv

load_dotenv()

# TradingView bağlantısını başlat
# Not: Kimlik bilgileri olmadan da çalışabilir ama sınırlıdır.
# Kullanıcı adı ve şifre ile anlık verilere (eğer hesabınızda varsa) erişebilirsiniz.
username = os.getenv("TV_USERNAME")
password = os.getenv("TV_PASSWORD")

tv = TvDatafeed(username, password)

def get_tv_stock_data(symbol: str):
    """TradingView üzerinden anlık hisse verisi çeker."""
    try:
        # BIST hisseleri için 'BIST:' prefix'i eklenir
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
            "change": 0.0, # TV verisinden hesaplanması gerekebilir
            "name": symbol,
            "currency": "TRY"
        }
    except Exception as e:
        print(f"TradingView Hatası: {e}")
        return None

def get_tv_akd_data(symbol: str):
    """
    TradingView'dan gerçek AKD (Aracı Kurum Dağılımı) verisi teknik olarak çekilemez 
    çünkü TV bu veriyi sağlamaz. Ancak hacim profili ve para girişi simülasyonu yapılabilir.
    """
    try:
        data = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_1_minute, n_bars=100)
        if data is None or data.empty:
            return None
            
        # Basit bir Para Giriş/Çıkış simülasyonu (Hacim ve Fiyat hareketine göre)
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
    """TradingView üzerinden geçmiş verileri çeker."""
    try:
        data = tv.get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=n_bars)
        return data
    except Exception as e:
        print(f"TradingView Hatası: {e}")
        return None
