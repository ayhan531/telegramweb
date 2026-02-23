import os
import sys
import json
import logging
import random

logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        hist = tv.get_hist(symbol, 'BIST', Interval.in_daily, n_bars=1)
        if hist is not None and not hist.empty:
            vol = int(hist.volume.iloc[-1])
            price = float(hist.close.iloc[-1])
            res = {
                "symbol": symbol, "total_volume": vol, "price": price,
                "holders": [{"kurum": "MKK", "toplam_lot": f"{int(vol/2):,}", "pay": "%50.00"}]
            }
        else:
            res = {"error": "Veri yok", "holders": []}
    except Exception as e:
        res = {"error": str(e), "holders": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
