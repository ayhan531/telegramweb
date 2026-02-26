import logging
import os
import matplotlib.pyplot as plt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, MenuButtonWebApp
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
from api.tv_api import get_unified_data, get_history_data
from api.real_akd_api import get_real_akd_data
from utils.chart_generator import create_stock_chart
import sqlite3
import asyncio
import pandas as pd

# Load environment variables (from .env if it exists, otherwise use environment)
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv() # Fallback to standard environment variables

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "❖ *DERINLIK & ANALIZ TERMINALI PRO*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "BIST, Kripto ve Emtia piyasalarında *gerçek zamanlı* ve *derinlemesine* analiz sistemine hoş geldiniz.\n\n"
        "Aşağıdaki butona tıklayarak derinlik, analiz, takas ve grafiklere *(Pro Veri Terminali)* kesintisiz olarak erişebilirsiniz.\n\n"
        "▰ *HIZLI KOMUTLAR*\n"
        "▪ `/derinlik [SEMBOL]` - Anlık Piyasa Özeti (Örn: THYAO)\n"
        "▪ `/grafik [SEMBOL]`   - YZ Destekli Teknik Analiz\n"
        "▪ `/akd [SEMBOL]`      - Aracı Kurum Dağılımı (Matriks)\n"
        "▪ `/alarm [SEMBOL] [FİYAT]` - Algoritmik Fiyat Alarmı\n"
        "▪ `/alarmlar`          - Aktif Alarmları Yönet\n"
        "▪ `/yardim`            - Sistem Dokümantasyonu\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    
    # Kullanicinin Render'da yanlislikla "WEBAPP_URL" degiskenini eski .pages.dev olarak 
    # kaydetmis olma ihtimaline karsi o degiskeni GORMEZDEN GELIYORUZ.
    # Render'in kendi verdigi RENDER_EXTERNAL_URL'yi veya sabit degeri kullaniyoruz:
    webapp_url = os.getenv("RENDER_EXTERNAL_URL", "https://telegramweb-gd62.onrender.com")
    keyboard = [
        [InlineKeyboardButton("▰ TERMINALI AC", web_app=WebAppInfo(url=webapp_url))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text, 
        reply_markup=reply_markup
    )

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "❖ *PRO KULLANIM REHBERI*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Gelişmiş veri terminali üzerinden sistemimize erişmektesiniz. Veri sorgulamak için sembol kodunu komutla birlikte girmeniz yeterlidir.\n\n"
        "▰ *ÖRNEK KULLANIMLAR*\n"
        "• Borsa İstanbul: `/derinlik THYAO`\n"
        "• Kripto Para: `/derinlik BTCUSDT`\n"
        "• Emtia / Altın: `/derinlik XAUUSD`\n"
        "• Teknik Analiz: `/grafik EREGL`\n"
        "• AKD Dökümü: `/akd ASTOR`\n\n"
        "❯ *İpucu:* Tüm özellikleri tam ekranda ve en yüksek hızda deneyimlemek için 'TERMINALI AC' butonunu kullanın."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

RELAY_URL = "http://127.0.0.1:8765"

async def call_relay(path: str):
    """Userbot relay servisine HTTP isteği atar. (fotoğraf veya metin)"""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{RELAY_URL}{path}", timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    ct = resp.content_type
                    if 'image' in ct:
                        return {"type": "photo", "data": await resp.read()}
                    else:
                        j = await resp.json()
                        return {"type": "text", "data": j.get("text", "")}
                else:
                    j = await resp.json()
                    return {"type": "error", "data": j.get("error", "Bilinmeyen hata")}
    except Exception as e:
        return {"type": "error", "data": str(e)}

async def derinlik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: `/derinlik THYAO`", parse_mode='Markdown')
        return

    symbol = context.args[0].upper()
    msg = await update.message.reply_text(f"▶ `{symbol}` derinlik verisi getiriliyor...", parse_mode='Markdown')

    result = await call_relay(f"/derinlik/{symbol}")

    await msg.delete()

    if result["type"] == "photo":
        import io
        caption = f"{symbol} — Derinlik (25 Kademe)\n© 2026 Analytical Data Terminal. Tüm Hakları Saklıdır."
        await update.message.reply_photo(
            photo=io.BytesIO(result["data"]),
            caption=caption
        )
    elif result["type"] == "text":
        await update.message.reply_text(
            f"▶ *{symbol} — Derinlik*\n\n`{result['data'][:3000]}`",
            parse_mode='Markdown'
        )
    else:
        # Fallback: yerel veri
        data = get_unified_data(symbol)
        if data and "error" not in data:
            text = (
                f"▶ *{symbol} — PİYASA*\n"
                f"`{'\u2500'*30}`\n"
                f"▪ *Fiyat:*   `{data['price']:.2f} ₺`\n"
                f"▪ *Açılış:* `{data.get('open','---')}`\n"
                f"▪ *Yüksek:* `{data.get('high','---')}`\n"
                f"▪ *Düşük:*  `{data.get('low','---')}`\n"
                f"▪ *Hacim:*  `{data.get('volume','---')}`\n"
                f"`{'\u2500'*30}`\n"
                f"❯ _© 2026 Analytical Data Terminal._"
            )
            await update.message.reply_text(text, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"_{symbol} verisi alınamadı. Lütfen tekrar deneyin._", parse_mode='Markdown')

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("HATA: Sembol girilmedi.")
        return
    
    symbol = context.args[0].upper()
    raw_hist = get_history_data(symbol)
    
    if not raw_hist:
        await update.message.reply_text(f"HATA: {symbol} gecmis verisi bulunamadi.")
        return
    
    # Chart expects a DataFrame
    hist = pd.DataFrame(raw_hist)
    hist['Date'] = pd.to_datetime(hist['date'])
    hist.set_index('Date', inplace=True)
    hist.rename(columns={'price': 'Close'}, inplace=True)
        
    chart_path = f"{symbol}_chart.png"
    if create_stock_chart(hist, symbol, chart_path):
        caption = f"TEKNIK ANALIZ: {symbol}\n© 2026 Analytical Data Terminal. Tüm Hakları Saklıdır."
        await update.message.reply_photo(photo=open(chart_path, 'rb'), caption=f"```\n{caption}\n```", parse_mode='MarkdownV2')
        os.remove(chart_path)
    else:
        await update.message.reply_text("HATA: Grafik olusturulamadi.")

async def akd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: `/akd THYAO`", parse_mode='Markdown')
        return

    symbol = context.args[0].upper()
    msg = await update.message.reply_text(f"▶ `{symbol}` AKD verisi getiriliyor...", parse_mode='Markdown')

    result = await call_relay(f"/akd/{symbol}")

    await msg.delete()

    if result["type"] == "photo":
        import io
        caption = f"{symbol} — Aracı Kurum Dağılımı\n© 2026 Analytical Data Terminal. Tüm Hakları Saklıdır."
        await update.message.reply_photo(
            photo=io.BytesIO(result["data"]),
            caption=caption
        )
    elif result["type"] == "text":
        await update.message.reply_text(
            f"▶ *{symbol} — AKD*\n\n`{result['data'][:3000]}`",
            parse_mode='Markdown'
        )
    else:
        # Fallback: yerel API
        data = await get_real_akd_data(symbol)
        if not data or not data.get('buyers'):
            await update.message.reply_text(
                f"_{symbol} AKD verisi alınamadı. Tekrar deneyin._",
                parse_mode='Markdown'
            )
            return
        text = f"▶ *{symbol} — ARACI KURUM DAĞILIMI*\n"
        text += f"`{'\u2500'*36}`\n"
        text += f"`{'KURUM':<18} {'ORAN':>6} {'NET LOT':>12}`\n"
        text += f"`{'\u2500'*36}`\n"
        for b in data.get('buyers', []):
            text += f"`{b['kurum'][:18]:<18} {str(b.get('oran','')):>6} {str(b.get('lot','')):>12}`\n"
        text += f"`{'\u2500'*36}`\n"
        for s in data.get('sellers', []):
            text += f"`{s['kurum'][:18]:<18} {str(s.get('oran','')):>6} {str(s.get('lot','')):>12}`\n"
        text += f"`{'\u2500'*36}`\n"
        text += f"❯ _© 2026 Analytical Data Terminal. Tüm Hakları Saklıdır._"
        await update.message.reply_text(text, parse_mode='Markdown')

# --- Alarm İşlemleri ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/database.sqlite')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

async def alarm_kur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: `/alarm [SEMBOL] [FIYAT]`\nÖrn: `/alarm THYAO 315.50`", parse_mode='Markdown')
        return
    
    symbol = context.args[0].upper()
    try:
        target_price = float(context.args[1].replace(',', '.'))
    except ValueError:
        await update.message.reply_text("HATA: Geçersiz fiyat formatı.")
        return

    # Mevcut fiyatı kontrol et (koşulu belirlemek için)
    data = get_unified_data(symbol)
    if "error" in data:
        await update.message.reply_text(f"HATA: {symbol} sembolü bulunamadı.")
        return
    
    current_price = data['price']
    condition = 'ABOVE' if target_price > current_price else 'BELOW'
    cond_text = "üzerine çıkınca" if condition == 'ABOVE' else "altına inince"

    user_id = str(update.effective_user.id)
    conn = get_db_connection()
    conn.execute("INSERT INTO alarms (user_id, symbol, target_price, condition) VALUES (?, ?, ?, ?)",
                 (user_id, symbol, target_price, condition))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✓ *ALARM KURULDU*\n{symbol} fiyatı {target_price} {cond_text} haber vereceğim.", parse_mode='Markdown')

async def alarmlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    conn = get_db_connection()
    rows = conn.execute("SELECT id, symbol, target_price, condition FROM alarms WHERE user_id = ? AND is_active = 1", (user_id,)).fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Aktif alarmınız bulunmuyor.")
        return

    text = "▰ *AKTİF ALARMLARINIZ*\n\n"
    for r in rows:
        cond = "▲" if r['condition'] == 'ABOVE' else "▼"
        text += f"ID: `{r['id']}` | {r['symbol']} | {cond} {r['target_price']}\n"
    
    text += "\nAlarm silmek için: `/alarmsil [ID]`"
    await update.message.reply_text(text, parse_mode='Markdown')

async def alarm_sil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Kullanım: `/alarmsil [ID]`")
        return
    
    alarm_id = context.args[0]
    user_id = str(update.effective_user.id)
    
    conn = get_db_connection()
    res = conn.execute("DELETE FROM alarms WHERE id = ? AND user_id = ?", (alarm_id, user_id))
    conn.commit()
    deleted = res.rowcount
    conn.close()

    if deleted:
        await update.message.reply_text(f"✓ Alarm `{alarm_id}` başarıyla silindi.", parse_mode='Markdown')
    else:
        await update.message.reply_text("HATA: Alarm bulunamadı veya size ait değil.")

async def alarm_check_loop(application):
    logging.info("Alarm kontrol döngüsü başlatıldı.")
    while True:
        try:
            conn = get_db_connection()
            alarms = conn.execute("SELECT * FROM alarms WHERE is_active = 1").fetchall()
            
            # Sembol bazlı grupla (Verimlilik için)
            symbols = list(set([a['symbol'] for a in alarms]))
            prices = {}
            for s in symbols:
                data = get_unified_data(s)
                if "price" in data:
                    prices[s] = data['price']
            
            for a in alarms:
                s = a['symbol']
                if s not in prices: continue
                
                curr = prices[s]
                target = a['target_price']
                cond = a['condition']
                
                triggered = False
                if cond == 'ABOVE' and curr >= target: triggered = True
                elif cond == 'BELOW' and curr <= target: triggered = True
                
                if triggered:
                    text = f"[!] *FİYAT ALARMI TETİKLENDİ!*\n\n*{s}* şu an *{curr}* seviyesinde.\n(Hedef: {target})"
                    await application.bot.send_message(chat_id=a['user_id'], text=text, parse_mode='Markdown')
                    conn.execute("UPDATE alarms SET is_active = 0 WHERE id = ?", (a['id'],))
                    conn.commit()
            
            conn.close()
        except Exception as e:
            logging.error(f"Alarm check error: {e}")
            
        await asyncio.sleep(60) # Her dakika kontrol et

async def post_init(application):
    # Arka plan görevini başlat
    asyncio.create_task(alarm_check_loop(application))
    webapp_url = os.getenv("RENDER_EXTERNAL_URL", "https://telegramweb-gd62.onrender.com")
    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Terminal", web_app=WebAppInfo(url=webapp_url))
        )
        logging.info(f"Yenilenen Menu Butonu URL'si basariyla ayarlandi: {webapp_url}")
    except Exception as e:
        logging.error(f"Failed to set menu button: {e}")

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    print(f"DEBUG: TELEGRAM_BOT_TOKEN status: {'Set' if token else 'NOT SET'}")
    
    if not token or token == "your_bot_token_here":
        print("CRITICAL ERROR: TELEGRAM_BOT_TOKEN is missing or default!")
        sys.exit(1)
    else:
        application = ApplicationBuilder().token(token).post_init(post_init).build()
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('yardim', yardim))
        application.add_handler(CommandHandler('derinlik', derinlik))
        application.add_handler(CommandHandler('grafik', grafik))
        application.add_handler(CommandHandler('akd', akd))
        application.add_handler(CommandHandler('alarm', alarm_kur))
        application.add_handler(CommandHandler('alarmlar', alarmlar))
        application.add_handler(CommandHandler('alarmsil', alarm_sil))
        
        print("Bot başlatılıyor...")
        application.run_polling(drop_pending_updates=True)
