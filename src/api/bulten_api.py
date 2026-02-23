"""
Bülten API - BIST100 Özet ve En Çok Artanlar/Azalanlar
Kaynak: Yahoo Finance (ücretsiz, gerçek anlık veri)
"""
import yfinance as yf
import json
import sys
from datetime import datetime

# BIST'in en aktif ve likit hisse listesi (Yahoo Finance'de stabil olanlar)
BIST_STOCKS = [
    'THYAO.IS', 'SASA.IS', 'EREGL.IS', 'GARAN.IS', 'ASELS.IS',
    'KCHOL.IS', 'BIMAS.IS', 'TUPRS.IS', 'ISCTR.IS', 'HALKB.IS',
    'AKBNK.IS', 'VAKBN.IS', 'FROTO.IS', 'TOASO.IS', 'PGSUS.IS',
    'PETKM.IS', 'SAHOL.IS', 'TCELL.IS', 'ENKAI.IS',
    'SOKM.IS', 'TAVHL.IS', 'EKGYO.IS', 'ARCLK.IS', 'SKBNK.IS', 'YKBNK.IS'
]

BIST_NAMES = {
    'THYAO.IS': 'THY', 'SASA.IS': 'SASA', 'EREGL.IS': 'EREGL',
    'GARAN.IS': 'GARAN', 'ASELS.IS': 'ASELS', 'KCHOL.IS': 'KCHOL',
    'BIMAS.IS': 'BIMAS', 'TUPRS.IS': 'TUPRS', 'ISCTR.IS': 'ISCTR',
    'HALKB.IS': 'HALKB', 'AKBNK.IS': 'AKBNK', 'VAKBN.IS': 'VAKBN',
    'FROTO.IS': 'FROTO', 'TOASO.IS': 'TOASO', 'PGSUS.IS': 'PGSUS',
    'PETKM.IS': 'PETKM', 'SAHOL.IS': 'SAHOL', 'TCELL.IS': 'TCELL', 
    'ENKAI.IS': 'ENKAI', 'SOKM.IS': 'SOKM', 'TAVHL.IS': 'TAVHL', 
    'EKGYO.IS': 'EKGYO', 'ARCLK.IS': 'ARCLK', 'SKBNK.IS': 'SKBNK', 
    'YKBNK.IS': 'YKBNK'
}


def get_bulten_data():
    """
    BIST 100 endeksi ve en çok artanlar/azalanlar.
    Tamamen gerçek Yahoo Finance verisi.
    """
    try:
        # BIST 100 endeksi
        bist100 = yf.Ticker('XU100.IS')
        # Use history to be safer than fast_info
        hist100 = bist100.history(period='2d')
        if hist100.empty:
            return {"error": "Endeks verisi alınamadı"}
            
        price = float(hist100['Close'].iloc[-1])
        prev_close = float(hist100['Close'].iloc[-2]) if len(hist100) > 1 else price
        change_val = price - prev_close
        change_pct = (change_val / prev_close * 100) if prev_close else 0

        # En çok artanlar/azalanlar
        data = yf.download(BIST_STOCKS, period='2d', interval='1d', progress=False, group_by='ticker')

        gainers = []
        losers = []
        all_changes = {}

        for sym in BIST_STOCKS:
            try:
                if sym in data:
                    s_data = data[sym]
                    if len(s_data) >= 2:
                        c_today = s_data['Close'].iloc[-1]
                        c_prev = s_data['Close'].iloc[-2]
                        if c_prev > 0:
                            all_changes[sym] = (c_today - c_prev) / c_prev * 100
            except:
                continue

        if all_changes:
            # Sort changes
            sorted_changes = sorted(all_changes.items(), key=lambda x: x[1], reverse=True)
            
            # Artanlar
            for sym, chg in sorted_changes[:5]:
                gainers.append({
                    "symbol": BIST_NAMES.get(sym, sym.split('.')[0]),
                    "change": f"+{chg:.2f}%"
                })
                
            # Azalanlar
            for sym, chg in sorted_changes[-5:]:
                losers.append({
                    "symbol": BIST_NAMES.get(sym, sym.split('.')[0]),
                    "change": f"{chg:.2f}%"
                })

        # Tarih
        now = datetime.now()
        months = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
                  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        date_str = f"{now.day} {months[now.month-1]} {days[now.weekday()]}"

        return {
            "index_name": "BIST 100",
            "price": f"{price:,.2f}".replace(',', '.'),
            "change": f"{change_pct:+.2f}%",
            "gainers": gainers,
            "losers": losers,
            "status": "POZİTİF" if change_pct >= 0 else "NEGATİF",
            "date": date_str
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    res = get_bulten_data()
    print(json.dumps(res, ensure_ascii=False))
