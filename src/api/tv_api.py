"""
Hisse Senedi Veri API'si
Kaynak: Yahoo Finance (ücretsiz, gerçek anlık veri)
"""
import yfinance as yf
import requests
import json
import sys

def get_tv_stock_data(symbol: str):
    """
    Hisse senedi anlık verisini çeker.
    BIST sembolü otomatik olarak .IS eki ile Yahoo Finance'den alınır.
    """
    try:
        yf_symbol = f"{symbol.upper()}.IS"
        ticker = yf.Ticker(yf_symbol)
        fi = ticker.fast_info

        price = fi['last_price']
        prev_close = fi['previous_close']
        change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0

        return {
            "price": round(float(price), 2),
            "open": round(float(fi.get('open', price)), 2),
            "high": round(float(fi.get('day_high', price)), 2),
            "low": round(float(fi.get('day_low', price)), 2),
            "volume": int(fi.get('last_volume', 0)),
            "change": round(float(change_pct), 2),
            "prev_close": round(float(prev_close), 2),
            "year_high": round(float(fi.get('year_high', 0)), 2),
            "year_low": round(float(fi.get('year_low', 0)), 2),
            "market_cap": fi.get('market_cap'),
            "name": symbol.upper(),
            "currency": "TRY"
        }
    except Exception as e:
        print(f"Hisse Veri Hatası ({symbol}): {e}", file=sys.stderr)
        return None


def get_tv_stock_history(symbol: str, n_bars=100):
    """
    Hisse senedi geçmiş verisini çeker (günlük).
    """
    try:
        yf_symbol = f"{symbol.upper()}.IS"
        ticker = yf.Ticker(yf_symbol)
        # n_bars ~= kaç günlük veri
        period = f"{max(n_bars, 30)}d"
        hist = ticker.history(period=period, interval='1d')
        if hist.empty:
            return None
        return hist.tail(n_bars)
    except Exception as e:
        print(f"Geçmiş Veri Hatası ({symbol}): {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sym = sys.argv[1].upper()
        res = get_tv_stock_data(sym)
        if res:
            # NaN değerleri temizle
            for k, v in res.items():
                if isinstance(v, float) and (v != v):
                    res[k] = None
            print(json.dumps(res))
        else:
            print(json.dumps({"error": "Veri bulunamadı"}))
