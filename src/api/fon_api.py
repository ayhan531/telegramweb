"""
Fon Veri API (BIST Yatırım Fonları & ETF'ler)
Kaynak: Yahoo Finance (ücretsiz, gerçek anlık veri)
"""
import yfinance as yf
import json
import sys

# BIST'te işlem gören en aktif borsa yatırım fonları (ETF)
ETF_LIST = {
    'GLDTR.IS': 'QNB Altın Fonu',
    'USDTR.IS': 'QNB Dolar Fonu',
    'Z30EA.IS': 'Ziraat Portföy BIST 30',
    'GMSTR.IS': 'Gümüş Borsa Yatırım Fonu',
    'ZGOLD.IS': 'Ziraat Portföy Altın',
}

def get_fon_data():
    """
    BIST'te işlem gören fonların (ETF) gerçek anlık verilerini çeker.
    """
    try:
        symbols = list(ETF_LIST.keys())
        data = yf.download(symbols, period='2d', interval='1d', progress=False, group_by='ticker')

        funds = []

        for sym in symbols:
            try:
                if sym in data:
                    s_data = data[sym]
                    if not s_data.empty:
                        price = float(s_data['Close'].iloc[-1])
                        prev_price = float(s_data['Close'].iloc[-2]) if len(s_data) > 1 else price
                        change_pct = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0

                        code = sym.replace('.IS', '')
                        funds.append({
                            "code": code,
                            "name": ETF_LIST.get(sym, code),
                            "change": ("+" if change_pct >= 0 else "") + f"{change_pct:.2f}%",
                            "color": "bg-yellow-600" if "ALTIN" in ETF_LIST[sym].upper() or "GOLD" in sym.upper() else "bg-blue-600",
                            "icon": code[0]
                        })
            except:
                continue

        return {"funds": funds}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    res = get_fon_data()
    print(json.dumps(res, ensure_ascii=False))
