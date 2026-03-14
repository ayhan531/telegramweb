import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_tv_technical_analysis(symbol, exchange="BIST"):
    sessionid = os.getenv("TV_SESSIONID")
    # TV uses different scanner URLs based on the market
    market = "turkey" if exchange == "BIST" else "global"
    url = f"https://scanner.tradingview.com/{market}/scan"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": "https://www.tradingview.com/",
        "Cookie": f"sessionid={sessionid}" if sessionid else ""
    }

    payload = {
        "symbols": {
            "tickers": [f"{exchange}:{symbol.upper()}"],
            "query": {"types": []}
        },
        "columns": [
            "Recommend.All",
            "RSI",
            "MACD.macd",
            "MACD.signal",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data['data']:
                d = data['data'][0]['d']
                rec_map = {
                    -1: "Güçlü Sat",
                    -0.5: "Sat",
                    0: "Nötr",
                    0.5: "Al",
                    1: "Güçlü Al"
                }
                # Mapping recommendation score to text
                score = d[0]
                rec_text = "Nötr"
                if score is not None:
                    if score <= -0.5: rec_text = "Güçlü Sat" if score <= -0.75 else "Sat"
                    elif score >= 0.5: rec_text = "Güçlü Al" if score >= 0.75 else "Al"
                
                return {
                    "recommendation": rec_text,
                    "rsi": f"{d[1]:.2f}" if d[1] else "---",
                    "macd": f"{d[2]:.2f}" if d[2] else "---",
                    "open": d[4],
                    "high": d[5],
                    "low": d[6],
                    "price": d[7],
                    "volume": d[8],
                    "source": "TradingView (Scanner API)"
                }
        return {"error": f"TV API Error {res.status_code}", "text": res.text[:200]}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    s = sys.argv[1] if len(sys.argv) > 1 else "THYAO"
    print(json.dumps(get_tv_technical_analysis(s), indent=2))
