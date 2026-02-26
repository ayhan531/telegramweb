"""
USERBOT RELAY SERVİSİ
=====================
Bizim botumuzdan sorgu gelince hedef bota (@ucretsizderinlikbot) iletir,
cevabı (fotoğraf veya metin) anlık olarak döndürür.
Dosya kaydetmez, periyodik tarama yapmaz. Tamamen anlık proxy.

Çalıştırma:
  pip install telethon aiohttp
  python3 userbot_relay.py
"""

import asyncio
import io
import time
import sys
from aiohttp import web
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

API_ID   = 37031232
API_HASH = "518b15f17950300182c1edf6921e7c92"
SESSION  = "akd_scraper_session"

TARGET_BOT = "ucretsizderinlikbot"
PORT       = 8765

# Aynı anda gelen sorgular çakışmasın diye lock
query_lock = asyncio.Lock()

client = TelegramClient(SESSION, API_ID, API_HASH)


async def relay_query(command: str) -> dict:
    """
    Hedef bota komutu gönder, cevabı bekle ve döndür.
    Döndürülen dict:
      { "type": "photo",   "data": <bytes> }
      { "type": "text",    "data": <str>   }
      { "type": "error",   "data": <str>   }
    """
    async with query_lock:
        try:
            me = await client.get_me()
            me_id = me.id

            # Komutu gönder
            await client.send_message(TARGET_BOT, command)

            # Botun cevabı için bekle (max 10 saniye)
            for attempt in range(10):
                await asyncio.sleep(1.2)
                messages = await client.get_messages(TARGET_BOT, limit=3)
                for msg in messages:
                    if msg.sender_id == me_id:
                        continue
                    # Fotoğraf cevabı
                    if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                        buf = io.BytesIO()
                        await client.download_media(msg, file=buf)
                        buf.seek(0)
                        return {"type": "photo", "data": buf.read()}
                    # Metin cevabı
                    if msg.text and len(msg.text) > 10:
                        return {"type": "text", "data": msg.text}

            return {"type": "error", "data": "Hedef bot cevap vermedi (timeout)"}

        except Exception as e:
            return {"type": "error", "data": str(e)}


# ──────────────────────────────────────────────
#  HTTP ENDPOINT'LERİ
# ──────────────────────────────────────────────

async def handle_akd(request: web.Request) -> web.Response:
    symbol = request.match_info.get("symbol", "").upper()
    if not symbol:
        return web.json_response({"error": "Sembol gerekli"}, status=400)

    print(f"[{time.strftime('%H:%M:%S')}] AKD relay → /akd {symbol}")
    result = await relay_query(f"/akd {symbol}")

    if result["type"] == "photo":
        return web.Response(body=result["data"], content_type="image/jpeg")
    elif result["type"] == "text":
        return web.json_response({"text": result["data"]})
    else:
        return web.json_response({"error": result["data"]}, status=502)


async def handle_derinlik(request: web.Request) -> web.Response:
    symbol = request.match_info.get("symbol", "").upper()
    if not symbol:
        return web.json_response({"error": "Sembol gerekli"}, status=400)

    print(f"[{time.strftime('%H:%M:%S')}] Derinlik relay → /derinlik {symbol}")
    result = await relay_query(f"/derinlik {symbol}")

    if result["type"] == "photo":
        return web.Response(body=result["data"], content_type="image/jpeg")
    elif result["type"] == "text":
        return web.json_response({"text": result["data"]})
    else:
        return web.json_response({"error": result["data"]}, status=502)


async def handle_health(request: web.Request) -> web.Response:
    me = await client.get_me()
    return web.json_response({"status": "ok", "account": me.first_name})


# ──────────────────────────────────────────────
#  BAŞLATMA
# ──────────────────────────────────────────────

async def main():
    print("=" * 52)
    print("  USERBOT RELAY SERVİSİ BAŞLATILIYOR")
    print(f"  Port: {PORT}  |  Hedef: @{TARGET_BOT}")
    print("=" * 52)

    await client.start()
    me = await client.get_me()
    print(f"✅ Telegram hesabı: {me.first_name} ({me.id})\n")

    app = web.Application()
    app.router.add_get("/akd/{symbol}",      handle_akd)
    app.router.add_get("/derinlik/{symbol}", handle_derinlik)
    app.router.add_get("/health",            handle_health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", PORT)
    await site.start()

    print(f"✅ HTTP Relay aktif → http://127.0.0.1:{PORT}")
    print(f"   /akd/THYAO     → @{TARGET_BOT}'a /akd THYAO gönderir")
    print(f"   /derinlik/THYAO → @{TARGET_BOT}'a /derinlik THYAO gönderir")
    print(f"\nBekliyor... (Ctrl+C ile durdur)\n")

    # Sonsuza kadar çalış
    await asyncio.Event().wait()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nRelay servisi kapatılıyor...")
    finally:
        loop.run_until_complete(client.disconnect())
        loop.close()
