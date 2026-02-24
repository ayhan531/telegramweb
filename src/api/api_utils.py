import os
import sys
import json
import logging
from datetime import datetime

def suppress_stdout_stderr():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

_original_stdout = sys.stdout
_original_stderr = sys.stderr

def run_script(func, *args, **kwargs):
    # Suppress output during execution
    _stdout = sys.stdout
    _stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        result = {"error": str(e)}
    
    # Restore and print JSON
    sys.stdout = _original_stdout
    sys.stderr = _original_stderr
    print(json.dumps(result, ensure_ascii=False))
