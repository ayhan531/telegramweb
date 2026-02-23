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
    
    symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        
        hist = tv.get_hist(symbol, 'BIST', Interval.in_1_minute, n_bars=50)
        # NOT: tvDatafeed üzerinden kurum bazlı (AKD) veri çekilememektedir.
        # Kullanıcı isteği üzerine sahte veri üretimi kaldırılmıştır.
        res = {"error": "Kurum bazlı AKD verisi bu kaynakta mevcut değil.", "buyers": [], "sellers": [], "total": []}
    except Exception as e:
        res = {"error": str(e), "buyers": [], "sellers": [], "total": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
