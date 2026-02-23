import os
import sys
import json
import logging

logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        ETF_LIST = {'GLDTR': 'Altın ETF', 'USDTR': 'Dolar ETF', 'Z30EA': 'BIST30 ETF', 'GMSTR': 'Gümüş ETF'}
        funds = []
        for sym, name in ETF_LIST.items():
            try:
                data = tv.get_hist(sym, 'BIST', Interval.in_daily, n_bars=2)
                if data is not None and not data.empty:
                    p = float(data.close.iloc[-1])
                    pc = float(data.close.iloc[-2]) if len(data) >= 2 else p
                    ch = ((p-pc)/pc*100) if pc>0 else 0
                    funds.append({"code": sym, "name": name, "change": f"{ch:+.2f}%", 
                                "color": "bg-yellow-600" if "GOLD" in sym.upper() else "bg-blue-600", "icon": sym[0]})
            except: continue
        
        if not funds:
             funds = [{"code": "GLDTR", "name": "Altın ETF", "change": "+0.00%", "color": "bg-yellow-600", "icon": "G"}]
        res = {"funds": funds}
    except Exception as e:
        res = {"error": str(e), "funds": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
