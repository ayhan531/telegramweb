"""
USERBOT RELAY v5 (PRIMARY: b0pt_bot)
=====================================
- b0pt_bot: ANA KAYNAK (AKD, Derinlik, Analiz, Takas vb.)
- ucretsizderinlikbot: YEDEK KAYNAK.
- Her iki bot birbirinin yedeği (fallback) olarak çalışır.
"""

import asyncio
import io
import sys
import os
import time
from aiohttp import web
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# Fotoğraf markalama modülünü içe aktar
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from image_brander import brand_image

API_ID   = 37031232
API_HASH = "518b15f17950300182c1edf6921e7c92"
SESSION  = os.path.join(os.path.dirname(__file__), "akd_scraper_session")

# Hedef botlar
PRIMARY_BOT  = "b0pt_bot"
FALLBACK_BOT = "ucretsizderinlikbot"
PORT         = 8765

query_lock = asyncio.Lock()
client = TelegramClient(SESSION, API_ID, API_HASH)

async def relay_query(command: str, period: str = None, target_bot: str = PRIMARY_BOT) -> dict:
    """Komutu gönderir, cevap alamazsa diğer botu dener."""
    async with query_lock:
        # Önce tercih edilen botu dene
        result = await _execute_query(command, period, target_bot)
        
        # Eğer hata varsa veya cevap yoksa diğer botu dene
        if result["type"] == "error":
            fallback = FALLBACK_BOT if target_bot == PRIMARY_BOT else PRIMARY_BOT
            print(f"  ⚠️ {target_bot} başarısız, {fallback} deneniyor...")
            result = await _execute_query(command, period, fallback)
            
        return result

async def _execute_query(command: str, period: str, target: str) -> dict:
    try:
        if not client.is_connected():
            await client.connect()
            
        me = await client.get_me()
        me_id = me.id

        print(f"[{time.strftime('%H:%M:%S')}] --> {target}: {command}")
        await client.send_message(target, command)

        bot_msg = None
        for attempt in range(12):
            await asyncio.sleep(1.0)
            messages = await client.get_messages(target, limit=3)
            for msg in messages:
                if msg.sender_id != me_id:
                    bot_msg = msg
                    break
            if bot_msg: break

        if not bot_msg:
            return {"type": "error", "data": "Cevap alınamadı."}

        # Periyot Butonları (Eğer varsa tıkla)
        if period and bot_msg.buttons:
            found_btn = False
            for row in bot_msg.buttons:
                for btn in row:
                    if period.lower() in btn.text.lower() or btn.text.lower() in period.lower():
                        await btn.click()
                        found_btn = True
                        break
                if found_btn: break
                
            if found_btn:
                await asyncio.sleep(4)
                # Güncel mesajı al
                msgs = await client.get_messages(target, limit=3)
                for m in msgs:
                    if m.sender_id != me_id and m.media:
                        bot_msg = m
                        break

        # Fotoğraf işleme
        if bot_msg.media and isinstance(bot_msg.media, (MessageMediaPhoto, MessageMediaDocument)):
            buf = io.BytesIO()
            await client.download_media(bot_msg, file=buf)
            buf.seek(0)
            return {"type": "photo", "data": buf.read()}
        
        if bot_msg.text:
            return {"type": "text", "data": bot_msg.text}

        return {"type": "error", "data": "Beklenen formatta veri gelmedi."}

    except Exception as e:
        return {"type": "error", "data": str(e)}

# --- HTTP Handlers ---

async def handle_akd(request):
    symbol = request.match_info.get("symbol", "").upper()
    period = request.query.get("period")
    result = await relay_query(f"/akd {symbol}", period=period)
    return prepare_response(result, symbol, f"AKD ({period or 'Günlük'})")

async def handle_derinlik(request):
    symbol = request.match_info.get("symbol", "").upper()
    result = await relay_query(f"/derinlik {symbol}")
    return prepare_response(result, symbol, "25 Kademe Derinlik")

async def handle_cmd(request):
    cmd = request.match_info.get("cmd", "")
    symbol = request.match_info.get("symbol", "").upper()
    result = await relay_query(f"/{cmd} {symbol}")
    
    titles = {
        "islem": "Anlık İşlemler",
        "teorik": "Teorik Eşleşme",
        "takas": "Takas Analizi",
        "sirketkarti": "Şirket Bilgi Kartı",
        "detay": "Hisse Detayları",
        "tum": "Toplu Analiz"
    }
    return prepare_response(result, symbol, titles.get(cmd, cmd.capitalize()))

def prepare_response(result, symbol, title):
    if result["type"] == "photo":
        branded = brand_image(result["data"], symbol=symbol, data_type=title)
        return web.Response(body=branded, content_type="image/jpeg")
    elif result["type"] == "text":
        return web.json_response({"text": result["data"]})
    else:
        return web.json_response({"error": result["data"]}, status=502)

async def handle_health(request):
    try:
        me = await client.get_me() if client.is_connected() else None
        return web.json_response({"status": "ok", "account": me.first_name if me else "disconnected"})
    except:
        return web.json_response({"status": "error"}, status=500)

async def start_relay():
    await client.start()
    app = web.Application()
    app.router.add_get("/akd/{symbol}", handle_akd)
    app.router.add_get("/derinlik/{symbol}", handle_derinlik)
    app.router.add_get("/cmd/{cmd}/{symbol}", handle_cmd)
    app.router.add_get("/health", handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", PORT)
    await site.start()
    print(f"🚀 Relay Aktif (Primary Bot: @{PRIMARY_BOT}): http://127.0.0.1:{PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(start_relay())
    except KeyboardInterrupt:
        print("\nKapatılıyor...")
