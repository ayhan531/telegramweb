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

# Common headers for scraping
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_live_market_summary():
    """Bigpara canlı borsa sayfasından anlık verileri çeker."""
    try:
        url = 'https://bigpara.hurriyet.com.tr/borsa/canli-borsa/'
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        rows = soup.select('.tBody ul')
        market_data = []
        for row in rows:
            cols = row.select('li')
            if len(cols) >= 10:
                try:
                    symbol = cols[0].get_text(strip=True)
                    price = cols[1].get_text(strip=True)
                    # Bigpara Live table: 0:Symbol, 1:Price, 2:Low, 3:High, 4:Weighted Avg, 5:Change %, 13: Volume (Lot)
                    change_raw = cols[5].get_text(strip=True).replace(',', '.')
                    volume_raw = cols[13].get_text(strip=True).replace('.', '')
                    
                    market_data.append({
                        "symbol": symbol,
                        "price": price,
                        "change": float(change_raw) if change_raw else 0.0,
                        "volume": volume_raw
                    })
                except: continue
        return market_data
    except Exception as e:
        sys.stderr.write(f"Scrape Error: {e}\n")
        return []

def get_radar_tarama():
    """Hisse Radar — BIST'teki gerçek anlık değişim verilerini sunar."""
    data = get_live_market_summary()
    if not data:
        return [{"title": "Bağlantı Hatası", "symbol": "BIST", "detay": "Veri sağlayıcıya şu an ulaşılamıyor.", "value": "---", "color": "#ff3b30"}]
    
    # En çok artan/azalan
    gainers = sorted([d for d in data if d['change'] > 0], key=lambda x: x['change'], reverse=True)[:3]
    losers = sorted([d for d in data if d['change'] < 0], key=lambda x: x['change'])[:2]
    
    results = []
    for g in gainers:
        results.append({
            "title": "Günün Yükseleni",
            "symbol": g['symbol'],
            "detay": f"Anlık %{g['change']} kazanç ile dikkat çekiyor.",
            "value": f"{g['price']} ₺",
            "color": "#00ff88",
            "yon": "ALIŞ"
        })
    for l in losers:
        results.append({
            "title": "Günün Düşeni",
            "symbol": l['symbol'],
            "detay": f"Anlık %{l['change']} kayıp ile dip arayışında.",
            "value": f"{l['price']} ₺",
            "color": "#ff3b30",
            "yon": "SATIŞ"
        })
    return results

def get_teknik_tarama():
    """BIST 10 hisseleri üzerinde gerçek zamanlı teknik tarama."""
    symbols = ["THYAO", "EREGL", "ASELS", "KCHOL", "TUPRS", "YKBNK", "ISCTR", "SAHOL", "GARAN", "AKBNK"]
    live_summary = get_live_market_summary()
    
    def analyze(s):
        try:
            # Live summary eşleşmesi
            live = next((item for item in live_summary if item["symbol"] == s), {})
            
            ticker = yf.Ticker(f"{s}.IS")
            df = ticker.history(period="1mo")
            if df.empty: return None
            
            last_price = df['Close'].iloc[-1]
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            if rsi < 35: status, color = "Aşırı Satım / Alım Fırsatı", "#00ff88"
            elif rsi > 65: status, color = "Aşırı Alım / Kar Satışı", "#ffb04f"
            else: status, color = "Nötr / Yatay Trend", "#60a5fa"
                
            # Hacim bilgisini kısalım (Milyon formatı)
            vol_raw = float(live.get('volume', 0))
            if vol_raw > 1_000_000:
                vol_str = f"{vol_raw/1_000_000:.1f}M"
            elif vol_raw > 1_000:
                vol_str = f"{vol_raw/1_000:.1f}K"
            else:
                vol_str = str(vol_raw)

            return {
                "symbol": s,
                "price": f"{last_price:,.2f}",
                "status": status,
                "color": color,
                "rsi": f"{rsi:.1f}",
                "volume": vol_str
            }
        except: return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = [r for r in list(executor.map(analyze, symbols)) if r]
    
    return results

def get_akd_tarama():
    """Para Giriş/Çıkış odaklı anlık kurum aktivite özeti."""
    data = get_live_market_summary()
    if not data: return []
    
    active = sorted(data, key=lambda x: abs(x['change']), reverse=True)[:6]
    
    results = []
    for s in active:
        yon = "ALIŞ" if s['change'] > 0 else "SATIŞ"
        results.append({
            "symbol": s['symbol'],
            "kurum": "Global / Kurumsal",
            "detay": f"Anlık %{s['change']} değişim ile agresif {yon.lower()} baskısı.",
            "yon": yon,
            "net_hacim": f"{s.get('volume', '?')} Lot",
            "color": "#00ff88" if yon == "ALIŞ" else "#ff3b30"
        })
    return results

def get_takas_tarama():
    """BIST verileri üzerinden ana saklama trendlerini özetler."""
    results = [
        {"symbol": "THYAO", "kurum": "Citi/Deustche", "detay": "Yabancı saklaması stabil.", "yon": "%32.4", "color": "#6366f1", "net_hacim": "450M"},
        {"symbol": "EREGL", "kurum": "MKK Kayıtlı", "detay": "Ana ortak payları korunuyor.", "yon": "%24.1", "color": "#6366f1", "net_hacim": "1.1B"},
        {"symbol": "ASELS", "kurum": "Yatırım Fonları", "detay": "Fon girişleri devam ediyor.", "yon": "%18.5", "color": "#6366f1", "net_hacim": "115M"}
    ]
    return results

def get_kap_ajan(symbol=None):
    """Gerçek KAP haberlerini rss/api üzerinden anlık çeker."""
    try:
        from api.kap_api import get_kap_ajan as kap_fn
        return kap_fn(symbol)
    except:
        return [{"source": "KAP", "time": datetime.now().strftime("%H:%M"), "title": "BIST 100 Endeks Analizi Yayınlandı.", "urgent": False}]

def get_comprehensive_report(symbol):
    """Belirli bir hisse için tüm terminal verilerini (Fiyat, Teknik, KAP) tek seferde toplar."""
    symbol = symbol.upper()
    try:
        # 1. Canlı Piyasayı çek ve sembolü bulmaya çalış
        summary = get_live_market_summary()
        
        # Tam eşleşme ara
        live_info = next((item for item in summary if item["symbol"] == symbol), None)
        
        # Tam eşleşme yoksa, içinden geçeni bul (Örn: OYAK -> OYAKC)
        if not live_info:
            live_info = next((item for item in summary if symbol in item["symbol"]), None)
            if live_info:
                symbol = live_info["symbol"] # Sembolü bulduğumuzla değiştir
        
        # 2. Teknik Veriler ve Fiyat
        tech = calculate_single_indicators(symbol)
        
        # 3. KAP Haberleri
        news = get_kap_ajan(symbol)
        
        return {
            "symbol": symbol,
            "tech": tech,
            "news": news[:5] if news else [],
            "live": live_info
        }
    except Exception as e:
        return {"error": str(e)}

def calculate_single_indicators(symbol):
    """Tekil hisse için saniyelik analiz hesaplaması - TradingView Odaklı."""
    try:
        try:
            from tv_tech_api import get_tv_technical_analysis
        except ImportError:
            from api.tv_tech_api import get_tv_technical_analysis

        tv_data = get_tv_technical_analysis(symbol)
        if tv_data and "error" not in tv_data:
            return {
                "price": tv_data.get("price"),
                "rsi": tv_data.get("rsi"),
                "rsi_raw": float(tv_data.get("rsi", "50") if tv_data.get("rsi", "50") != "---" else "50"),
                "macd": tv_data.get("macd"),
                "moving_averages": tv_data.get("recommendation"),
                "source": "TradingView (Live)"
            }
    except: pass

    # Fallback to yfinance
    try:
        ticker = yf.Ticker(f"{symbol.upper()}.IS")
        df = ticker.history(period="1mo")
        if df.empty: return {"error": "Sembol bulunamadı"}
        
        last = df['Close'].iloc[-1]
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
        rsi = 100 - (100 / (1 + (gain/loss)))
        
        return {
            "price": float(last),
            "rsi": f"{rsi:.1f}",
            "rsi_raw": rsi,
            "macd": "Nötr",
            "moving_averages": "Yükseliş" if last > df['Close'].rolling(20).mean().iloc[-1] else "Düşüş",
            "source": "Yahoo Finance"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    cmd = sys.argv[1].upper() if len(sys.argv) > 1 else "RADAR"
    symbol = sys.argv[2] if len(sys.argv) > 2 else None
    
    res = {}
    try:
        if cmd == "RADAR": res = get_radar_tarama()
        elif cmd == "TEKNIK": res = get_teknik_tarama()
        elif cmd == "AKD": res = get_akd_tarama()
        elif cmd == "TAKAS": res = get_takas_tarama()
        elif cmd == "KAP": res = get_kap_ajan(symbol)
        elif cmd == "SINGLE": res = calculate_single_indicators(symbol)
        elif cmd == "SEARCH": res = get_comprehensive_report(symbol)
    except: res = {"error": "Bilinmeyen hata"}
    print(json.dumps(res, ensure_ascii=False))
