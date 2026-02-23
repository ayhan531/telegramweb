import os
import sys
import json
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Hide warnings
logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

def get_data_for_symbol(tv, exchange, sym, name, interval, n_bars):
    try:
        data = tv.get_hist(symbol=sym, exchange=exchange, interval=interval, n_bars=n_bars)
        if data is not None and not data.empty:
            p = float(data.close.iloc[-1])
            pc = float(data.close.iloc[-2]) if len(data) >= 2 else p
            ch = ((p - pc) / pc * 100) if pc > 0 else 0
            return {
                "symbol": name, 
                "price": f"{p:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), 
                "change": f"{ch:+.2f}%",
                "change_val": ch,
                "raw_price": p,
                "raw_symbol": sym
            }
    except:
        pass
    return None

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        targets = [
            ('BIST', 'THYAO', 'THY'), ('BIST', 'SASA', 'SASA'), ('BIST', 'EREGL', 'EREGL'),
            ('BIST', 'ASELS', 'ASELS'), ('BIST', 'GARAN', 'GARAN'),
            ('BINANCE', 'BTCUSDT', 'Bitcoin'), ('BINANCE', 'ETHUSDT', 'Ethereum'),
            ('FX_IDC', 'XAUUSD', 'Altın'), ('FX_IDC', 'USOIL', 'Petrol')
        ]
        
        # Parallel fetch
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(lambda x: get_data_for_symbol(tv, x[0], x[1], x[2], Interval.in_daily, 2), targets))
        
        results = [r for r in results if r is not None]
        
        bist_sum = [r for r in results if r['raw_symbol'] in ['THYAO', 'SASA', 'EREGL', 'ASELS', 'GARAN']]
        crypto_sum = [r for r in results if r['raw_symbol'] in ['BTCUSDT', 'ETHUSDT']]
        comm_sum = [r for r in results if r['raw_symbol'] in ['XAUUSD', 'USOIL']]
        
        # Index data
        idx_data = tv.get_hist('XU100', 'BIST', Interval.in_daily, n_bars=2)
        idx_p, idx_c, status = "0,00", "+0,00%", "NÖTR"
        if idx_data is not None and not idx_data.empty:
            p = float(idx_data.close.iloc[-1])
            pc = float(idx_data.close.iloc[-2]) if len(idx_data) >= 2 else p
            ch = ((p-pc)/pc*100)
            idx_p = f"{p:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            idx_c = f"{ch:+.2f}%"
            status = "POZİTİF" if ch >= 0 else "NEGATİF"

        # Gainers/Losers from results
        bist_all = sorted(bist_sum, key=lambda x: x['change_val'], reverse=True)
        
        res = {
            "index_name": "BIST 100", "price": idx_p, "change": idx_c, "status": status,
            "date": datetime.now().strftime("%d %m %Y"),
            "bist_summary": bist_sum,
            "crypto_summary": crypto_sum,
            "commodity_summary": comm_sum,
            "gainers": bist_all[:5], 
            "losers": sorted(bist_all, key=lambda x: x['change_val'])[:5]
        }
    except Exception as e:
        res = {"error": str(e), "bist_summary": [], "crypto_summary": [], "commodity_summary": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
