import yfinance as ticker
import pandas as pd

def get_stock_data(symbol: str):
    """Hisse senedi verilerini çeker (BIST için .IS son eki eklenir)"""
    if not symbol.endswith(".IS"):
        symbol = f"{symbol.upper()}.IS"
    
    stock = ticker.Ticker(symbol)
    info = stock.info
    
    if not info or 'regularMarketPrice' not in info:
        return None
        
    return {
        "price": info.get("regularMarketPrice"),
        "open": info.get("regularMarketOpen"),
        "high": info.get("dayHigh"),
        "low": info.get("dayLow"),
        "volume": info.get("volume"),
        "change": info.get("regularMarketChangePercent"),
        "name": info.get("longName", symbol),
        "currency": info.get("currency", "TRY"),
        "market_cap": info.get("marketCap")
    }

def get_stock_history(symbol: str, period="1mo", interval="1d"):
    """Hisse senedi geçmiş verilerini çeker"""
    if not symbol.endswith(".IS"):
        symbol = f"{symbol.upper()}.IS"
    
    stock = ticker.Ticker(symbol)
    hist = stock.history(period=period, interval=interval)
    return hist
