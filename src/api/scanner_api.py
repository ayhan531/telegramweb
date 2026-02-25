import os
import sys
import json
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Gerçek KAP modülü
try:
    from api.kap_api import get_kap_ajan as _real_kap_ajan
except ImportError:
    try:
        from kap_api import get_kap_ajan as _real_kap_ajan
    except ImportError:
        _real_kap_ajan = None

# Common headers for scraping
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def calculate_manual_rsi(series, period=14):
    if len(series) < period: return pd.Series([50]*len(series))
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_symbol_technical(symbol):
    try:
        s = f"{symbol}.IS"
        df = yf.download(s, period="3mo", interval="1d", progress=False)
        if df.empty or len(df) < 50: return None
        
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        
        rsi = calculate_manual_rsi(close).iloc[-1]
        sma20 = close.rolling(window=20).mean().iloc[-1]
        sma50 = close.rolling(window=50).mean().iloc[-1]
        price = close.iloc[-1]
        
        # Volume Check
        vol_sma = df['Volume'].rolling(window=10).mean().iloc[-1]
        last_vol = df['Volume'].iloc[-1]
        vol_score = "Yüksek" if last_vol > vol_sma * 1.5 else "Normal"
        
        if rsi < 35: status, color = "Aşırı Satım / Alım Fırsatı", "#00ff88"
        elif price > sma20 and price > sma50: status, color = "Güçlü Yükseliş", "#00ff88"
        elif price < sma20 and price < sma50: status, color = "Güçlü Düşüş", "#ff3b30"
        elif rsi > 65: status, color = "Aşırı Alım / Kar Satışı", "#ffb04f"
        else: status, color = "Trende Giriyor", "#60a5fa"
            
        return {
            "symbol": symbol,
            "price": f"{price:,.2f}",
            "status": status,
            "color": color,
            "rsi": f"{rsi:.1f}",
            "volume": vol_score
        }
    except: return None

def get_teknik_tarama():
    symbols = [
        "THYAO", "EREGL", "ASELS", "KCHOL", "SAHOL", "BIMAS", "TUPRS", "YKBNK", "AKBNK", "SISE", 
        "SASA", "HEKTS", "DOAS", "FROTO", "PETKM", "KOZAL", "PGSUS", "ARCLK", "TOASO", "ENKAI",
        "GARAN", "ISCTR", "HALKB", "VAKBN", "EKGYO", "DOHOL", "TKFEN", "SOKM", "MGROS", "TTKOM"
    ]
    results = []
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = list(executor.map(get_symbol_technical, symbols))
        results = [f for f in futures if f is not None]
    
    # Fallback if yfinance fails
    if len(results) < 5:
        results = []
    
    # Sort by RSI
    results.sort(key=lambda x: float(x['rsi']))
    return results

def get_akd_tarama():
    return []

def get_takas_tarama():
    return []

def get_kap_ajan(symbol=None):
    """Gerçek KAP bildirimleri - kap_api.py modülünü kullanır."""
    if _real_kap_ajan:
        try:
            results = _real_kap_ajan(symbol)
            if results:
                return results
        except Exception:
            pass
    
    # Fallback: kap_api import edilemezse boş döndür
    return []


def calculate_single_indicators(symbol):
    try:
        s = f"{symbol.upper()}.IS"
        df = yf.download(s, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 50: return {"error": "Veri eksik"}
        
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]

        rsi_series = calculate_manual_rsi(close)
        rsi_val = rsi_series.iloc[-1]
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        sma20 = close.rolling(window=20).mean().iloc[-1]
        sma50 = close.rolling(window=50).mean().iloc[-1]
        current_price = close.iloc[-1]

        rsi_text = f"{rsi_val:.1f} "
        if rsi_val > 70: rsi_text += "(Aşırı Alım)"
        elif rsi_val < 30: rsi_text += "(Aşırı Satım)"
        else: rsi_text += "(Nötr)"

        macd_text = "Al Sinyali" if macd.iloc[-1] > signal.iloc[-1] else "Sat Sinyali"
        
        if current_price > sma20 and current_price > sma50: ma_text = "Güçlü Al"
        elif current_price > sma20: ma_text = "Al"
        elif current_price < sma50: ma_text = "Güçlü Sat"
        else: ma_text = "Sat"

        return {
            "rsi": rsi_text,
            "macd": macd_text,
            "moving_averages": ma_text,
            "rsi_raw": float(rsi_val),
            "macd_raw": float(macd.iloc[-1]),
            "price": float(current_price),
            "akd": [],
            "kap_news": []
        }
    except Exception as e: return {"error": str(e)}

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        arg = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
        
        res = {}
        if arg == "TEKNIK":
            res = {"results": get_teknik_tarama()}
        elif arg == "AKD":
            res = {"results": get_akd_tarama()}
        elif arg == "TAKAS":
            res = {"results": get_takas_tarama()}
        elif arg == "KAP":
            res = {"results": get_kap_ajan()}
        else:
            res = calculate_single_indicators(arg)
    except Exception as e:
        res = {"error": str(e), "results": []}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
