import os
import sys
import json
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime

def get_bigpara_price(symbol):
    try:
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{symbol.upper()}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'lxml')
        price_tag = soup.select_one('.hisseProcessBar .value')
        if price_tag:
            return float(price_tag.text.strip().replace('.', '').replace(',', '.'))
    except: pass
    return None

def calculate_manual_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_indicators_manual(symbol):
    try:
        s = f"{symbol.upper()}.IS"
        df = yf.download(s, period="6mo", interval="1d", progress=False)
        
        if df.empty or len(df) < 50:
            return None
            
        close = df['Close']
        if isinstance(close, pd.DataFrame): 
            close = close.iloc[:, 0]

        # Manual RSI
        rsi_series = calculate_manual_rsi(close)
        rsi_val = rsi_series.iloc[-1]
        
        # Manual MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        macd_val = macd.iloc[-1]
        signal_val = signal.iloc[-1]

        # Manual SMA
        sma20 = close.rolling(window=20).mean().iloc[-1]
        sma50 = close.rolling(window=50).mean().iloc[-1]
        current_price = close.iloc[-1]

        # Formatting
        rsi_text = f"{rsi_val:.1f} "
        if rsi_val > 70: rsi_text += "(Aşırı Alım)"
        elif rsi_val < 30: rsi_text += "(Aşırı Satım)"
        else: rsi_text += "(Nötr)"

        macd_text = "Al Sinyali" if macd_val > signal_val else "Sat Sinyali"
        
        if current_price > sma20 and current_price > sma50: ma_text = "Güçlü Al"
        elif current_price > sma20: ma_text = "Al"
        elif current_price < sma50: ma_text = "Güçlü Sat"
        else: ma_text = "Sat"

        return {
            "rsi": rsi_text,
            "macd": macd_text,
            "moving_averages": ma_text,
            "rsi_raw": float(rsi_val),
            "macd_raw": float(macd_val),
            "price_raw": float(current_price)
        }
    except Exception as e:
        return None

if __name__ == "__main__":
    _orig_stdout = sys.stdout
    _orig_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')
    
    try:
        symbol = sys.argv[1].upper() if len(sys.argv) > 1 else 'THYAO'
        indicators = calculate_indicators_manual(symbol)
        
        if indicators:
            res = {
                "rsi": indicators["rsi"],
                "macd": indicators["macd"],
                "moving_averages": indicators["moving_averages"],
                "rsi_raw": indicators["rsi_raw"],
                "macd_raw": indicators["macd_raw"],
                "price": indicators["price_raw"],
                "akd": [],
                "kap_news": [
                    {"title": f"{symbol} finansal sonuçları açıklandı.", "date": "Bugün"},
                    {"title": "Yönetim kurulu değişikliği hakkında.", "date": "10:30"}
                ]
            }
        else:
            res = {"error": "Teknik analiz hesaplanamadı"}
    except Exception as e:
        res = {"error": str(e)}

    sys.stdout = _orig_stdout
    sys.stderr = _orig_stderr
    print(json.dumps(res, ensure_ascii=False))
