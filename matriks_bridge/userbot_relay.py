"""
USERBOT RELAY v7 (PHOTO-ONLY FOR DERINLIK/AKD)
==============================================
- ucretsizderinlikbot: 1. Sırada (Derinlik fotoğrafı için en iyisi)
- b0pt_bot: 2. Sırada (Güçlü yedek)
- Metin cevapları derinlik/akd için reddedilir, fotoğraf gelene kadar botlar taranır.
"""

import asyncio
import io
import sys
import os
import time
from aiohttp import web
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from image_brander import brand_image

API_ID   = 37031232
API_HASH = "518b15f17950300182c1edf6921e7c92"
SESSION  = os.path.join(os.path.dirname(__file__), "akd_scraper_session")

# Hangi komut hangi bottan çalişiyor (test sonuçlarına göre güncellendi)
BOT_GROUPS = {
    "default":      ["ucretsizderinlikbot", "b0pt_bot", "xFinans_bot"],
    "depth":        ["ucretsizderinlikbot", "b0pt_bot"],
    "akd":          ["ucretsizderinlikbot", "b0pt_bot"],
    "islem":        ["b0pt_bot", "xFinans_bot"],
    "teorik":       ["b0pt_bot", "xFinans_bot"],
    "takas":        ["b0pt_bot", "xFinans_bot"],
    "sirketkarti":  ["b0pt_bot", "xFinans_bot"],
    "detay":        ["b0pt_bot", "xFinans_bot"],
    "tum":          ["b0pt_bot", "xFinans_bot"],
}

PORT = 8765

query_lock = asyncio.Lock()
client = TelegramClient(SESSION, API_ID, API_HASH)

async def relay_query(command: str, period: str = None, force_photo: bool = False, group: str = "default") -> dict:
    """Sırayla tüm botları dener, başarılı olan ilk sonucu döner."""
    async with query_lock:
        bot_list = BOT_GROUPS.get(group, BOT_GROUPS["default"])
        for bot in bot_list:
            print(f"\n🔍 Sorgulanıyor: @{bot} | Komut: {command}")
            result = await _execute_query(command, period, bot)
            
            # Eğer fotoğraf lazımsa ama metin geldiyse pas geç, diğer bota bak
            if force_photo and result["type"] != "photo":
                print(f"⚠️ @{bot} metin verdi, fotoğraf bekleniyor. Diğer bota geçiliyor...")
                continue
                
            if result["type"] != "error":
                return result
            
        return {"type": "error", "data": "Hiçbir bot uygun veri dönmedi."}

async def _execute_query(command: str, period: str, target: str) -> dict:
    try:
        symbol = command.split()[-1] if len(command.split()) > 1 else ""
        if not client.is_connected(): await client.connect()
        me = await client.get_me()
        me_id = me.id

        # Önceki en son mesajın ID'sini al (Sadece yeni mesajları yakalamak için)
        last_msgs = await client.get_messages(target, limit=1)
        last_id = last_msgs[0].id if last_msgs else 0

        actual_cmd = command
        # Botlara göre komut düzeltmeleri
        if "sirketkarti" in actual_cmd:
            if target == "b0pt_bot": actual_cmd = actual_cmd.replace("sirketkarti", "sirketkartı")
            if target == "hisseyorumbot": actual_cmd = actual_cmd.replace("/sirketkarti", "/sirket")
        
        if target == "hisseyorumbot" and "tum" in actual_cmd:
            actual_cmd = actual_cmd.replace("/tum", "/rapor")

        print(f"[{time.strftime('%H:%M:%S')}] --> @{target}: {actual_cmd} (Last ID: {last_id})")
        await client.send_message(target, actual_cmd)

        bot_msg = None
        # Max 20 saniye bekle (Bazı botlar yavaş olabilir)
        for attempt in range(20):
            await asyncio.sleep(1.0)
            # SADECE komutumuzdan sonra gelen mesajlara bak (id > last_id)
            messages = await client.get_messages(target, limit=5)
            for msg in messages:
                if msg.sender_id == me_id: continue
                if msg.id <= last_id: continue # Eski mesajları/reklamları atla
                
                # --- REKLAM / AD FİLTRESİ ---
                msg_content = (msg.text or "").lower()
                if msg.media and hasattr(msg.media, 'caption') and msg.media.caption:
                    msg_content += " " + msg.media.caption.lower()
                
                is_ad = any(k in msg_content for k in ["best brands", "reklam", "sponsor", "t.me/", "satın al"])
                has_symbol = symbol.lower() in msg_content if symbol else False
                
                if is_ad and not has_symbol:
                    print(f"🚫 Reklam engellendi (ID: {msg.id})")
                    continue

                # Fotoğraf yakalama (Öncelikli)
                if msg.media and isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                    bot_msg = msg
                    break
                
                # Eğer daha önce fotoğraf bulamadıysak ve uzun/alakalı bir metin varsa al
                if not bot_msg and msg.text and len(msg.text) > 40:
                    if "bekle" not in msg.text.lower() and "hazırlanıyor" not in msg.text.lower():
                        bot_msg = msg
            
            if bot_msg and hasattr(bot_msg, 'media') and bot_msg.media:
                break

        if not bot_msg:
            return {"type": "error", "data": "Cevap alınamadı veya çok yavaş."}

        # Periyot Tıklama (AKD için)
        if period and bot_msg.buttons:
            found_btn = False
            for row in bot_msg.buttons:
                for btn in row:
                    if period.lower() in btn.text.lower():
                        await btn.click()
                        found_btn = True
                        break
                if found_btn: break
            
            if found_btn:
                # Buton ID'sini kaydet
                btn_click_id = bot_msg.id
                for a in range(10):
                    await asyncio.sleep(1.5)
                    msgs = await client.get_messages(target, limit=5)
                    for m in msgs:
                        # Buton tıklamasından sonra gelen YENİ fotoğrafı bekle
                        if m.sender_id != me_id and m.id >= btn_click_id and m.media:
                            bot_msg = m
                            break
                    if bot_msg.media: break

        # Çıktı Üretme
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

# --- Sunucu Handlerları ---
async def handle_akd(request):
    symbol = request.match_info.get("symbol", "").upper()
    period = request.query.get("period")
    result = await relay_query(f"/akd {symbol}", period=period, force_photo=True, group="akd")
    return prepare_response(result, symbol, f"AKD ({period or 'Günlük'})")

async def handle_derinlik(request):
    symbol = request.match_info.get("symbol", "").upper()
    result = await relay_query(f"/derinlik {symbol}", force_photo=True, group="default")
    return prepare_response(result, symbol, "25 Kademe Derinlik")

async def handle_cmd(request):
    cmd = request.match_info.get("cmd", "")
    symbol = request.match_info.get("symbol", "").upper()
    period = request.query.get("period")
    
    # Takas için varsayılan periyot (Eğer verilmediyse direkt görüntü gelsin diye)
    if cmd == "takas" and not period:
        period = "Günlük"
    
    # Her komut için hangi grubun kullanılacağını belirle
    group = cmd if cmd in BOT_GROUPS else "default"
    
    # Fotoğraf zorunlu olanlar (Metin gelirse pas geçilir)
    # Not: 'tum' ve 'detay' bazı botlarda metin döner, kabul ediyoruz.
    photo_required = cmd in ["islem", "teorik", "takas"]
    
    result = await relay_query(f"/{cmd} {symbol}", period=period, force_photo=photo_required, group=group)
    
    titles = {"islem":"İşlemler","teorik":"Teorik","takas":"Takas","sirketkarti":"Şirket Kartı","detay":"Detay","tum":"Rapor"}
    return prepare_response(result, symbol, titles.get(cmd, cmd.upper()))

def prepare_response(result, symbol, title):
    if result["type"] == "photo":
        from image_brander import brand_image
        branded = brand_image(result["data"], symbol=symbol, data_type=title)
        return web.Response(body=branded, content_type="image/jpeg")
    elif result["type"] == "text":
        return web.json_response({"text": result["data"]})
    else:
        return web.json_response({"error": result.get("data", "Hata")}, status=502)

async def main():
    await client.start()
    app = web.Application()
    app.router.add_get("/akd/{symbol}", handle_akd)
    app.router.add_get("/derinlik/{symbol}", handle_derinlik)
    app.router.add_get("/cmd/{cmd}/{symbol}", handle_cmd)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "127.0.0.1", PORT).start()
    print(f"🚀 DERİNLİK RELAY v8 AKTİF → http://127.0.0.1:{PORT}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

