import sys
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Try relative and absolute imports
try:
    from tv_tech_api import get_tv_technical_analysis
except ImportError:
    try:
        from api.tv_tech_api import get_tv_technical_analysis
    except ImportError:
        # Fallback path if run from root
        sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))
        from tv_tech_api import get_tv_technical_analysis

# List of important BIST stocks to monitor for signals
BIST_MONITOR_LIST = [
    "THYAO", "EREGL", "ASELS", "KCHOL", "TUPRS", "YKBNK", "ISCTR", "SAHOL", "GARAN", "AKBNK",
    "SISE", "BIMAS", "HEKTS", "SASA", "GUBRF", "KOZAL", "ODAS", "PETKM", "ASTOR", "KONTR"
]

def scan_symbol(symbol):
    try:
        data = get_tv_technical_analysis(symbol)
        if "error" in data:
            return None
        
        signals = []
        rsi = float(data.get("rsi", "50") if data.get("rsi") != "---" else "50")
        rec = data.get("recommendation", "Nötr")
        
        # 1. RSI Signals
        if rsi < 30:
            signals.append({"type": "RSI_OVERSOLD", "label": "Aşırı Satım (Alım Fırsatı)", "color": "#00ff88", "strength": "Strong"})
        elif rsi > 70:
            signals.append({"type": "RSI_OVERBOUGHT", "label": "Aşırı Alım (Kar Satışı)", "color": "#ff3b30", "strength": "Strong"})
            
        # 2. Recommendation Signals
        if "Güçlü Al" in rec:
            signals.append({"type": "STRONG_BUY", "label": "Güçlü Alım Sinyali", "color": "#00ff88", "strength": "Strong"})
        elif "Güçlü Sat" in rec:
            signals.append({"type": "STRONG_SELL", "label": "Güçlü Satış Sinyali", "color": "#ff3b30", "strength": "Strong"})

        if signals:
            return {
                "symbol": symbol,
                "price": data.get("price"),
                "rsi": rsi,
                "recommendation": rec,
                "signals": signals,
                "time": time.strftime("%H:%M:%S")
            }
    except:
        pass
    return None

def main():
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = [r for r in list(executor.map(scan_symbol, BIST_MONITOR_LIST)) if r]
    
    print(json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    main()
