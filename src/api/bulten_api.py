"""
Bülten API - Çoklu Piyasa Özeti (BIST, Kripto, Emtia)
Kaynak: TradingView / Yahoo Finance
"""
import yfinance as yf
import json
import sys
from datetime import datetime

# Sembol listeleri
BIST_STOCKS = ['THYAO.IS', 'SASA.IS', 'EREGL.IS', 'GARAN.IS', 'ASELS.IS']
CRYPTO_STOCKS = ['BTC-USD', 'ETH-USD', 'SOL-USD']
COMMODITY_STOCKS = ['GC=F', 'SI=F', 'CL=F'] # Gold, Silver, Crude Oil

BIST_NAMES = {'THYAO.IS': 'THY', 'SASA.IS': 'SASA', 'EREGL.IS': 'EREGL', 'GARAN.IS': 'GARAN', 'ASELS.IS': 'ASELS'}
CRYPTO_NAMES = {'BTC-USD': 'Bitcoin', 'ETH-USD': 'Ethereum', 'SOL-USD': 'Solana'}
COMMODITY_NAMES = {'GC=F': 'Altın (Ons)', 'SI=F': 'Gümüş (Ons)', 'CL=F': 'Petrol (WTI)'}

def get_market_summary(symbols, names):
    summary = []
    try:
        data = yf.download(symbols, period='2d', interval='1d', progress=False, group_by='ticker')
        for sym in symbols:
            try:
                if sym in data:
                    s_data = data[sym]
                    if not s_data.empty:
                        price = float(s_data['Close'].iloc[-1])
                        prev_price = float(s_data['Close'].iloc[-2]) if len(s_data) > 1 else price
                        change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                        
                        summary.append({
                            "symbol": names.get(sym, sym),
                            "price": f"{price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                            "change": f"{change_pct:+.2f}%"
                        })
            except: continue
    except: pass
    return summary

def get_bulten_data():
    """
    Tüm piyasalar için günlük özet.
    """
    try:
        # BIST 100
        bist100 = yf.Ticker('XU100.IS')
        hist100 = bist100.history(period='2d')
        price = 0
        change_pct = 0
        if not hist100.empty:
            price = float(hist100['Close'].iloc[-1])
            prev_close = float(hist100['Close'].iloc[-2]) if len(hist100) > 1 else price
            change_pct = (price - prev_close) / prev_close * 100

        # Market Summaries
        bist_gainers = get_market_summary(BIST_STOCKS, BIST_NAMES)
        crypto_summary = get_market_summary(CRYPTO_STOCKS, CRYPTO_NAMES)
        commodity_summary = get_market_summary(COMMODITY_STOCKS, COMMODITY_NAMES)

        # Tarih
        now = datetime.now()
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        date_str = f"{now.day} {months[now.month-1]} {days[now.weekday()]}"

        return {
            "index_name": "BIST 100",
            "price": f"{price:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "change": f"{change_pct:+.2f}%",
            "bist_summary": bist_gainers,
            "crypto_summary": crypto_summary,
            "commodity_summary": commodity_summary,
            "status": "POZİTİF" if change_pct >= 0 else "NEGATİF",
            "date": date_str
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_bulten_data()
    print(json.dumps(res, ensure_ascii=False))
