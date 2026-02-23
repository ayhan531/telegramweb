import os
import sys
import json
import logging
from concurrent.futures import ThreadPoolExecutor

logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

def get_etf_data(tv, sym):
    try:
        data = tv.get_hist(symbol=sym, exchange='FX_IDC', interval=Interval.in_daily, n_bars=2)
        if data is not None and not data.empty:
            p = float(data.close.iloc[-1])
            pc = float(data.close.iloc[-2]) if len(data) >= 2 else p
            ch = ((p - pc) / pc * 100) if pc > 0 else 0
            return {
                "code": sym, 
                "name": sym, # Basitleştirilmiş
                "change": f"{ch:+.2f}%", 
                "color": "bg-yellow-600" if "GOLD" in sym.upper() or "XAU" in sym.upper() else "bg-blue-600",
                "icon": sym[0]
            }
    except:
        return None

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        etf_list = ['GLDTR', 'USDTR', 'GUMUS', 'ZRE20', 'KCHOL', 'THYAO'] # Örnek liste
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            funds = list(executor.map(lambda s: get_etf_data(tv, s), etf_list))
        
        funds = [f for f in funds if f is not None]
        res = {"funds": funds}
    except Exception as e:
        res = {"error": str(e), "funds": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
