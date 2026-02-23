"""
Bülten API - Çoklu Piyasa Özeti (BIST, Kripto, Emtia)
Kaynak: TradingView (tvDatafeed)
"""
from tvDatafeed import TvDatafeed, Interval
import json
import sys
from datetime import datetime

# TradingView bağlantısı
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

# Sembol listeleri ve borsa eşleştirmeleri
MARKETS = {
    'BIST': {
        'exchange': 'BIST',
        'symbols': {
            'THYAO': 'THY',
            'SASA': 'SASA',
            'EREGL': 'EREGL',
            'GARAN': 'GARAN',
            'ASELS': 'ASELS'
        }
    },
    'CRYPTO': {
        'exchange': 'BINANCE',
        'symbols': {
            'BTCUSDT': 'Bitcoin',
            'ETHUSDT': 'Ethereum',
            'SOLUSDT': 'Solana'
        }
    },
    'COMMODITY': {
        'exchange': 'FX_IDC',
        'symbols': {
            'XAUUSD': 'Altın (Ons)',
            'XAGUSD': 'Gümüş (Ons)',
            'USOIL': 'Petrol (WTI)'
        }
    }
}

def get_market_summary(market_key):
    summary = []
    m_info = MARKETS[market_key]
    exchange = m_info['exchange']
    symbols_dict = m_info['symbols']
    
    for sym, name in symbols_dict.items():
        try:
            # Günlük değişim için 2 günlük bar çekelim (daha hızlı ve tutarlı)
            data = safe_get_hist(symbol=sym, exchange=exchange, interval=Interval.in_daily, n_bars=2)
            if data is not None and len(data) >= 1:
                price = float(data['close'].iloc[-1])
                prev_close = float(data['close'].iloc[-2]) if len(data) >= 2 else price
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                
                summary.append({
                    "symbol": name,
                    "price": f"{price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                    "change": f"{change_pct:+.2f}%"
                })
        except: continue
    return summary

def get_bulten_data():
    """
    Tüm piyasalar için günlük özet - TradingView tabanlı.
    """
    try:
        # BIST 100 Endeksi
        price_bist = 0
        change_bist = 0
        try:
            b100 = safe_get_hist(symbol='XU100', exchange='BIST', interval=Interval.in_daily, n_bars=2)
            if b100 is not None and not b100.empty:
                price_bist = float(b100['close'].iloc[-1])
                prev_bist = float(b100['close'].iloc[-2]) if len(b100) >= 2 else price_bist
                change_bist = ((price_bist - prev_bist) / prev_bist * 100)
        except: pass

        # Piyasa Özeti Çekimleri
        return {
            "index_name": "BIST 100",
            "price": f"{price_bist:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "change": f"{change_bist:+.2f}%",
            "bist_summary": get_market_summary('BIST'),
            "crypto_summary": get_market_summary('CRYPTO'),
            "commodity_summary": get_market_summary('COMMODITY'),
            "status": "POZİTİF" if change_bist >= 0 else "NEGATİF",
            "date": datetime.now().strftime("%d %m %Y") # Basitleştirilmiş tarih
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_bulten_data()
    print(json.dumps(res, ensure_ascii=False))
