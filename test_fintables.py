import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import sys

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-blink-features=AutomationControlled'])
        context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
        page = await context.new_page()
        
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("Visiting Fintables sirketler/THYAO/araci-kurum-dagilimi...")
        try:
            await page.goto("https://fintables.com/sirketler/THYAO/araci-kurum-dagilimi", wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(5000)
            html = await page.content()
            
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")
            
            if tables:
                for i, table in enumerate(tables):
                    print(f"--- Table {i} ---")
                    rows = table.find_all('tr')
                    for row in rows[:5]:
                        cols = row.find_all(['td', 'th'])
                        print([c.text.strip() for c in cols])
            else:
                print("No tables found. Page text preview:")
                print(soup.text[:500])
        except Exception as e:
            print("Error:", e)
        finally:
            await browser.close()

asyncio.run(main())
