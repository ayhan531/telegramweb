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
        # NOT: tvDatafeed üzerinden saklama (Takas) verisi çekilememektedir.
        # Kullanıcı isteği üzerine sahte veri üretimi kaldırılmıştır.
        res = {"error": "Saklama (Takas) verisi bu kaynakta mevcut değil.", "holders": []}
    except Exception as e:
        res = {"error": str(e), "holders": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
