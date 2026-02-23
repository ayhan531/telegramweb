import os
import sys
import json
import logging

logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

def detect_exchange(symbol: str):
    symbol = symbol.upper()
    crypto = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'AVAX', 'DOT', 'DOGE', 'SHIB', 'LINK']
    if any(c in symbol for c in crypto) or symbol.endswith('USDT'): return 'BINANCE'
    forex = ['XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDTRY', 'GA']
    if any(fc in symbol for fc in forex): return 'FX_IDC'
    return 'BIST'

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        # GA Özel Hesaplama (Sessiz modda)
        if symbol in ['GA', 'GRAMALTIN']:
            ex = 'FX_IDC'
            xau = tv.get_hist('XAUUSD', ex, Interval.in_1_minute, 1)
            usd = tv.get_hist('USDTRY', ex, Interval.in_1_minute, 1)
            if xau is not None and usd is not None:
                p = (xau.close.iloc[-1] / 31.10347) * usd.close.iloc[-1]
                res = {"price": round(p, 2), "change": 0.0, "name": "Gram Altın", "exchange": "Calc"}
            else: res = {"error": "GA veri yok"}
        else:
            ex = detect_exchange(symbol)
            data = tv.get_hist(symbol, ex, Interval.in_1_minute, n_bars=1)
            if data is not None and not data.empty:
                latest = data.iloc[-1]
                res = {"price": round(float(latest.close), 2), "change": 0.0, "name": symbol, "exchange": ex}
            else:
                res = {"error": "Sembol bulunamadı"}
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
