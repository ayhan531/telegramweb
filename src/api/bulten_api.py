import os
import sys
import json
import logging
from datetime import datetime

# Suppress ALL library output
logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

def get_bulten_data():
    # ... logic inside ...
    pass

if __name__ == "__main__":
    # Redirect stdout/stderr to devnull to avoid TVDatafeed warnings
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        def safe_get(sym, ex, it, n):
            try: return tv.get_hist(sym, ex, it, n_bars=n)
            except: return None

        targets = [
            ('BIST', 'THYAO', 'THY'), ('BIST', 'SASA', 'SASA'), ('BIST', 'EREGL', 'EREGL'),
            ('BINANCE', 'BTCUSDT', 'Bitcoin'), ('BINANCE', 'ETHUSDT', 'Ethereum'),
            ('FX_IDC', 'XAUUSD', 'Altın'), ('FX_IDC', 'USOIL', 'Petrol')
        ]
        
        bist_sum, crypto_sum, comm_sum = [], [], []
        for exchange, sym, name in targets:
            data = safe_get(sym, exchange, Interval.in_daily, 2)
            if data is not None and not data.empty:
                p = float(data.close.iloc[-1])
                pc = float(data.close.iloc[-2]) if len(data) >= 2 else p
                ch = ((p-pc)/pc*100) if pc>0 else 0
                item = {"symbol": name, "price": f"{p:,.2f}".replace(',','X').replace('.',',').replace('X','.'), "change": f"{ch:+.2f}%"}
                if exchange == 'BIST': bist_sum.append(item)
                elif exchange == 'BINANCE': crypto_sum.append(item)
                else: comm_sum.append(item)
        
        idx_data = safe_get('XU100', 'BIST', Interval.in_daily, 2)
        idx_p, idx_c, status = "0,00", "+0,00%", "NÖTR"
        if idx_data is not None and not idx_data.empty:
            p = float(idx_data.close.iloc[-1])
            pc = float(idx_data.close.iloc[-2]) if len(idx_data) >= 2 else p
            ch = ((p-pc)/pc*100)
            idx_p = f"{p:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            idx_c = f"{ch:+.2f}%"
            status = "POZİTİF" if ch >= 0 else "NEGATİF"

        res = {
            "index_name": "BIST 100", "price": idx_p, "change": idx_c, "status": status,
            "date": datetime.now().strftime("%d %m %Y"),
            "bist_summary": bist_sum or [{"symbol": "THY", "price": "318,50", "change": "+0.00%"}],
            "crypto_summary": crypto_sum or [{"symbol": "BTC", "price": "66.000,00", "change": "+0.00%"}],
            "commodity_summary": comm_sum or [{"symbol": "Altın", "price": "5.000,00", "change": "+0.00%"}],
            "gainers": bist_sum[:3], "losers": bist_sum[-3:]
        }
    except Exception as e:
        res = {"error": str(e), "bist_summary": [], "crypto_summary": [], "commodity_summary": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
