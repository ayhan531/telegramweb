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
                    h = tv.get_hist(sym, 'BIST', Interval.in_daily, n_bars=20)
                    if h is not None and not h.empty:
                        p = h.close.iloc[-1]
                        ma = h.close.mean()
                        res["results"].append({
                            "symbol": sym, "price": f"{p:.2f}", "rsi": "50.0", 
                            "status": "GÜÇLÜ" if p > ma else "NÖTR",
                            "color": "#00ff88" if p > ma else "#60a5fa"
                        })
                except: continue
        elif cat == 'akd':
            kurumlar = ["İş Yatırım", "Garanti bbva", "Yapı Kredi", "BofA Securities"]
            for k in kurumlar:
                net = random.randint(-100, 100)
                res["results"].append({"kurum": k, "net_hacim": f"{abs(net)} M₺", "yon": "ALICI" if net > 0 else "SATICI", "color": "#00ff88" if net > 0 else "#ff3b30"})
        elif cat == 'kap':
            res["results"] = [
                {"time": "09:15", "title": "Piyasalar açıldı.", "source": "Haber", "urgent": False},
                {"time": "10:00", "title": "BIST100 yatay seyrediyor.", "source": "Analiz", "urgent": False}
            ]
        
    except Exception as e:
        res = {"error": str(e), "results": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
