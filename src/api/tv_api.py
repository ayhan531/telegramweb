"""
Çoklu Piyasa Veri API'si (TradingView tabanlı)
Kaynak: TradingView (tvDatafeed)
Desteklenen Pazarlar: BIST, Kripto (Binance), Emtia/Forex (FX_IDC)
"""
from tvDatafeed import TvDatafeed, Interval
import json
import sys
import os

# TradingView bağlantısını başlat (nologin)
tv = TvDatafeed()

def detect_exchange(symbol: str):
    """
    Sembol ismine göre muhtemel borsayı tespit eder.
    """
    symbol = symbol.upper()
    
    # Kripto Para Kontrolü (Binance)
    # BTCUSDT, ETHUSDT vb. veya sadece BTC, ETH
    crypto_symbols = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'DOGE', 'SHIB', 'LINK']
    if any(crypto in symbol for crypto in crypto_symbols) or symbol.endswith('USDT'):
        return 'BINANCE'
    
    # Emtia / Forex Kontrolü
    # XAUUSD (Altın), XAGUSD (Gümüş), USOIL, EURUSD vb.
    forex_commodities = ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDTRY', 'GA']
    if any(fc in symbol for fc in forex_commodities):
        return 'FX_IDC'
    
    # Varsayılan: BIST
    return 'BIST'

def get_tv_stock_data(symbol: str):
    """
    TradingView üzerinden anlık veri çeker.
    Gram Altın (GA) için XAUUSD ve USDTRY üzerinden anlık hesaplama yapar.
    """
    try:
        symbol = symbol.upper()
        
        # Gram Altın (GA) Özel Hesaplama
        if symbol == 'GA' or symbol == 'GRAMALTIN':
            # Ons Altın ve Dolar/TL verilerini çek
            xau = tv.get_hist(symbol='XAUUSD', exchange='FX_IDC', interval=Interval.in_1_minute, n_bars=1)
            usdtry = tv.get_hist(symbol='USDTRY', exchange='FX_IDC', interval=Interval.in_1_minute, n_bars=1)
            
            if xau is not None and not xau.empty and usdtry is not None and not usdtry.empty:
                price_xau = float(xau['close'].iloc[-1])
                price_usdtry = float(usdtry['close'].iloc[-1])
                
                # Formül: (Ons / 31.10347) * (USD/TRY)
                price_ga = (price_xau / 31.10347) * price_usdtry
                
                # Önceki günün kapanışını hesapla (yüzde değişim için)
                xau_d = tv.get_hist(symbol='XAUUSD', exchange='FX_IDC', interval=Interval.in_daily, n_bars=2)
                usdtry_d = tv.get_hist(symbol='USDTRY', exchange='FX_IDC', interval=Interval.in_daily, n_bars=2)
                
                prev_price = price_ga
                if len(xau_d) >= 2 and len(usdtry_d) >= 2:
                    prev_ga = (xau_d['close'].iloc[-2] / 31.10347) * usdtry_d['close'].iloc[-2]
                    prev_price = prev_ga
                
                change_pct = ((price_ga - prev_price) / prev_price * 100) if prev_price else 0
                
                return {
                    "price": round(price_ga, 2),
                    "open": round(price_ga, 2),
                    "high": round(price_ga, 2),
                    "low": round(price_ga, 2),
                    "volume": 0,
                    "change": round(float(change_pct), 2),
                    "prev_close": round(float(prev_price), 2),
                    "name": "Gram Altın",
                    "exchange": "Hesaplanan",
                    "currency": "TRY"
                }

        exchange = detect_exchange(symbol)
        
        # tvDatafeed n_bars=1 ile son barı çeker
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_1_minute, n_bars=1)
        
        if data is None or data.empty:
            # Borsa tespiti yanlış olabilir, alternatif olarak FX_IDC dene (Foreks/Emtia için)
            if exchange != 'FX_IDC':
                data = tv.get_hist(symbol=symbol, exchange='FX_IDC', interval=Interval.in_1_minute, n_bars=1)
                if data is not None and not data.empty:
                    exchange = 'FX_IDC'
            
        if data is None or data.empty:
            return None

        latest = data.iloc[-1]
        
        # Önceki kapanış için 2 bar çekelim
        hist_2 = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=2)
        prev_close = latest['close'] # Varsayılan
        if hist_2 is not None and len(hist_2) >= 2:
            prev_close = hist_2['close'].iloc[-2]
        
        change_pct = ((latest['close'] - prev_close) / prev_close * 100) if prev_close else 0

        return {
            "price": round(float(latest['close']), 2),
            "open": round(float(latest['open']), 2),
            "high": round(float(latest['high']), 2),
            "low": round(float(latest['low']), 2),
            "volume": int(latest['volume']),
            "change": round(float(change_pct), 2),
            "prev_close": round(float(prev_close), 2),
            "name": symbol,
            "exchange": exchange,
            "currency": "TRY" if exchange == 'BIST' else "USD"
        }
    except Exception as e:
        print(f"TradingView Veri Hatası ({symbol}): {e}", file=sys.stderr)
        return None

def get_tv_stock_history(symbol: str, n_bars=100):
    """
    TradingView üzerinden geçmiş verisi çeker.
    """
    try:
        symbol = symbol.upper()
        exchange = detect_exchange(symbol)
        data = tv.get_hist(symbol=symbol, exchange=exchange, interval=Interval.in_daily, n_bars=n_bars)
        return data
    except Exception as e:
        print(f"TradingView Geçmiş Hatası ({symbol}): {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sym = sys.argv[1].upper()
        res = get_tv_stock_data(sym)
        if res:
            # NaN temizliği
            for k, v in res.items():
                if isinstance(v, float) and (v != v):
                    res[k] = None
            print(json.dumps(res, ensure_ascii=False))
        else:
            print(json.dumps({"error": "Veri bulunamadı"}))
