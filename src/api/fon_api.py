"""
Fon Veri API (BIST Yatırım Fonları & ETF'ler)
Kaynak: TradingView (tvDatafeed)
"""
from tvDatafeed import TvDatafeed, Interval
import json
import sys

# TradingView bağlantısı
tv = TvDatafeed()

def safe_get_hist(symbol, exchange, interval, n_bars, retries=3):
    """Bağlantı hatalarına karşı güvenli veri çekme."""
    for i in range(retries):
        try:
            data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            if data is not None and not data.empty:
                return data
        except:
            pass
    return None

# BIST'te işlem gören en aktif borsa yatırım fonları (ETF)
ETF_LIST = {
    'GLDTR': 'QNB Finansportföy Altın',
    'USDTR': 'QNB Finansportföy Dolar',
    'Z30EA': 'Ziraat Portföy BIST 30',
    'GMSTR': 'Gümüş Borsa Yatırım Fonu',
    'ZGOLD': 'Ziraat Portföy Altın',
    'Fİ1': 'OYAK Portföy Birinci Fon',
    'INVEO': 'Inveo Portföy Birinci Fon'
}

def get_fon_data():
    try:
        funds = []
        for symbol, name in ETF_LIST.items():
            try:
                data = safe_get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_1_minute, n_bars=1)
                hist_d = safe_get_hist(symbol=symbol, exchange='BIST', interval=Interval.in_daily, n_bars=2)
                
                if data is not None and not data.empty:
                    latest = data.iloc[-1]
                    price = float(latest['close'])
                    
                    prev_close = price
                    if hist_d is not None and len(hist_d) >= 2:
                        prev_close = float(hist_d['close'].iloc[-2])
                    
                    change_pct = ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0

                    funds.append({
                        "code": symbol,
                        "name": name,
                        "change": ("+" if change_pct >= 0 else "") + f"{change_pct:.2f}%",
                        "color": "bg-yellow-600" if "ALTIN" in name.upper() or "GOLD" in symbol.upper() else "bg-blue-600",
                        "icon": symbol[0]
                    })
            except:
                continue

        return {"funds": funds}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_fon_data()
    print(json.dumps(res, ensure_ascii=False))
