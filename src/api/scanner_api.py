import os
import sys
import json
import logging
import random
from datetime import datetime

logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        cat = sys.argv[1] if len(sys.argv) > 1 else 'teknik'
        res = {"results": []}

        if cat == 'teknik':
            symbols = ['THYAO', 'SASA', 'EREGL', 'GARAN', 'ASELS']
            for sym in symbols:
                try:
                    h = tv.get_hist(sym, 'BIST', Interval.in_daily, n_bars=30)
                    if h is not None and not h.empty:
                        p = h.close.iloc[-1]
                        ma = h.close.mean()
                        
                        # Basit Teknik Durum (Gerçek verilere dayalı)
                        status = "GÜÇLÜ" if p > ma else "ZAYIF"
                        res["results"].append({
                            "symbol": sym, "price": f"{p:.2f}", "rsi": "---", 
                            "status": status,
                            "color": "#00ff88" if status == "GÜÇLÜ" else "#ff3b30"
                        })
                except: continue
        elif cat == 'akd':
            # AKD Taraması için gerçek kurum verisi mevcut değil, boş dönülüyor.
            res["results"] = []
        elif cat == 'kap':
            res["results"] = []
        
    except Exception as e:
        res = {"error": str(e), "results": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
