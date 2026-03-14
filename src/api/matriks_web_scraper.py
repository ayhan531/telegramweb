import os
import asyncio
import json
import sys
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(root_dir, '.env'))

USER = os.getenv("MATRIKS_WEB_USER")
PASS = os.getenv("MATRIKS_WEB_PASS")
BASE_URL = os.getenv("MATRIKS_WEB_URL", "https://web.matriksdata.com")

# Session file to skip login
STATE_FILE = os.path.join(root_dir, "data", "matriks_web_state.json")

async def get_matriks_data(symbol, mode="quote"):
    """
    Matriks Web üzerinden veri çeker.
    mode: 'quote', 'depth', 'akd'
    """
    if not USER or USER == "your_username":
        return {"error": "Lütfen .env dosyasına MATRIKS_WEB_USER ve MATRIKS_WEB_PASS ekleyin."}

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        
        # Load state if exists
        context_args = {}
        if os.path.exists(STATE_FILE):
            context_args["storage_state"] = STATE_FILE
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        try:
            # Go to site
            await page.goto(BASE_URL)
            
            # Check if login is needed
            if await page.query_selector("input#mxcustom1"):
                print("DEBUG: Giriş yapılıyor...")
                await page.fill("input#mxcustom1", USER)
                await page.fill("input#mxcustom2", PASS)
                await page.click("button.primary-button.k-button-solid-primary")
                
                # Wait for login success (look for search bar or some post-login element)
                # This might need adjustment based on real login behavior (2FA etc)
                await page.wait_for_timeout(5000) 
                
                # Save state
                await context.storage_state(path=STATE_FILE)
            
            # TODO: Implement navigation to specific symbol and extraction
            # This is complex because Matriks Web is a SPA with canvases/heavy JS
            # For now, this is a skeleton. We'd need to find the search input,
            # type the symbol, and then scrape the resulting tables.
            
            # Example (Hypothetical):
            # await page.fill(".header-search-input", symbol)
            # await page.press(".header-search-input", "Enter")
            # await page.wait_for_selector(".depth-table")
            
            return {"status": "success", "message": f"{symbol} için Web Scraper altyapısı hazır. (Geliştirme aşamasında)"}

        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()

if __name__ == "__main__":
    symbol = sys.argv[1] if len(sys.argv) > 1 else "THYAO"
    result = asyncio.run(get_matriks_data(symbol))
    print(json.dumps(result, ensure_ascii=False))
