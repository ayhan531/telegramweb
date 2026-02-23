"""
Standardize API Output and Suppress Warnings
"""
import os
import sys
import json
import logging
from datetime import datetime

# Tüm kütüphane çıktılarını bastır
def suppress_stdout_stderr():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Logger'ları sustur
logging.getLogger('tvDatafeed').setLevel(logging.CRITICAL)

_original_stdout = sys.stdout
_original_stderr = sys.stderr

def run_script(func, *args, **kwargs):
    # Başlangıçta bastır
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        from tvDatafeed import TvDatafeed, Interval
        tv = TvDatafeed()
        result = func(tv, *args, **kwargs)
    except Exception as e:
        result = {"error": str(e)}
    
    # Sonunda geri yükle ve JSON'ı bas
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr
    print(json.dumps(result, ensure_ascii=False))

# Bu yapıyı tüm scriptlerde kullanacağız.
