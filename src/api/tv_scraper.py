import asyncio
import os
import json
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def get_tv_quote_browser(symbol):
    sessionid = os.getenv("TV_SESSIONID")
    if not sessionid:
        return {"error": "TV_SESSIONID not found"}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        
        # Inject cookie
        await context.add_cookies([{
            'name': 'sessionid',
            'value': sessionid,
            'domain': '.tradingview.com',
            'path': '/'
        }])
        
        page = await context.new_page()
        # Go to symbol page
        url = f"https://www.tradingview.com/symbols/BIST-{symbol}/"
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector(".last-0-3-1", timeout=10000) # Price selector might vary
            
            price = await page.inner_text(".last-0-3-1")
            change = await page.inner_text(".change-0-3-1")
            
            return {
                "price": price,
                "change": change,
                "symbol": symbol,
                "source": "TradingView (Browser)"
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()

def get_tv_quote(symbol):
    return asyncio.run(get_tv_quote_browser(symbol))

if __name__ == "__main__":
    import sys
    sym = sys.argv[1] if len(sys.argv) > 1 else "THYAO"
    print(json.dumps(get_tv_quote(sym), indent=2))
