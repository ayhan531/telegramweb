"""
PARİBU MENKUL DEĞER  —  Profesyonel Veri Terminali
Telegram Bot Ana Modülü
"""
import logging
import os
import asyncio
import sys
import io
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv

# ─── UTF-8 Windows ────────────────────────────────────────────────────────────
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='ignore')

# ─── Path & Env ───────────────────────────────────────────────────────────────
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir    = os.path.dirname(current_dir)
env_path    = os.path.join(root_dir, '.env')
load_dotenv(env_path) if os.path.exists(env_path) else load_dotenv()
sys.path.insert(0, current_dir)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── Branding ─────────────────────────────────────────────────────────────────
BRAND     = "PARİBU MENKUL DEĞER"
TAGLINE   = "Profesyonel Veri Terminali"
DIVIDER   = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
FOOTER    = f"© {datetime.now().year} {BRAND}  |  Lisanslı Bist Veri Terminali"

# Unicode ikon seti (emoji yok)
I = {
    "terminal": "▣", "ok": "▸", "err": "▪", "load": "▷",
    "radar":    "◉", "teknik": "◈", "akd": "◆", "takas": "◎",
    "kap":      "◇", "chart":  "▤", "depth": "■", "bullet": "›",
    "up":       "▲", "down":   "▼", "neutral": "◼", "alert": "◈",
}

# ─── Thread Pool (API çağrıları için) ─────────────────────────────────────────
executor = ThreadPoolExecutor(max_workers=4)

# ─── Lazy API Importları ──────────────────────────────────────────────────────
def _import(module, fn):
    try:
        import importlib
        mod = importlib.import_module(f"api.{module}")
        return getattr(mod, fn)
    except Exception as e:
        logger.warning(f"[Import] api.{module}.{fn} yüklenemedi: {e}")
        return None

# ─── Yardımcı: mesaj başlığı ──────────────────────────────────────────────────
def header(icon_key: str, title: str) -> str:
    return (
        f"*{BRAND}*\n"
        f"{I['terminal']}  {TAGLINE}\n"
        f"{DIVIDER}\n"
        f"{I.get(icon_key, I['ok'])}  *{title}*\n"
        f"{DIVIDER}"
    )

def footer_block() -> str:
    return f"{DIVIDER}\n_{FOOTER}_"

# ─────────────────────────────────────────────────────────────────────────────
#  MATRIKS UI SCRAPER (Ekran Görüntüsü)
# ─────────────────────────────────────────────────────────────────────────────
async def call_matriks_ui(symbol: str, hotkey: str, window_part: str):
    try:
        script      = os.path.join(root_dir, 'matriks_bridge', 'universal_scraper.py')
        safe_part   = "".join(x for x in window_part if x.isalnum())
        output_path = os.path.join(root_dir, 'data', 'matriks', f"{symbol}_{safe_part}.png")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if os.path.exists(output_path):
            try: os.remove(output_path)
            except: pass

        proc = await asyncio.create_subprocess_exec(
            'python', script, symbol, hotkey, window_part, output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

        if os.path.exists(output_path):
            return {"type": "photo", "path": output_path}

        err = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
        logger.error(f"Scraper: {err[:200]}")
        return {"type": "error", "data": "Terminal veriyi göndermedi. MatriksIQ açık mı?"}

    except asyncio.TimeoutError:
        return {"type": "error", "data": "Zaman aşımı (60s) — MatriksIQ yanıt vermedi."}
    except Exception as e:
        return {"type": "error", "data": str(e)}


async def matriks_command(update: Update, context: ContextTypes.DEFAULT_TYPE,
                          hotkey: str, window_part: str, title: str, icon: str):
    if not context.args:
        await update.message.reply_text(
            f"{header('err', 'Kullanım Hatası')}\n\n"
            f"{I['bullet']}  `/{update.message.text.split()[0][1:]} THYAO`\n\n"
            f"{footer_block()}",
            parse_mode='Markdown'
        )
        return

    symbol = context.args[0].upper()
    msg = await update.message.reply_text(
        f"{header('load', title)}\n\n"
        f"{I['load']}  Sembol  :  `{symbol}`\n"
        f"{I['load']}  Durum   :  MatriksIQ terminaline bağlanılıyor...\n\n"
        f"{footer_block()}",
        parse_mode='Markdown'
    )

    result = await call_matriks_ui(symbol, hotkey, window_part)

    if result["type"] == "photo":
        await msg.delete()
        caption = (
            f"*{BRAND}*  {I.get(icon, I['ok'])}\n"
            f"{DIVIDER}\n"
            f"{I['ok']}  Sembol    :  `{symbol}`\n"
            f"{I['ok']}  Veri Türü :  *{title}*\n"
            f"{I['ok']}  Saat      :  `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"{DIVIDER}\n"
            f"_{FOOTER}_"
        )
        with open(result["path"], 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode='Markdown')
    else:
        await msg.edit_text(
            f"{header('err', 'Terminal Hatası')}\n\n"
            f"{I['err']}  Sembol  :  `{symbol}`\n"
            f"{I['err']}  Hata    :  _{result['data']}_\n\n"
            f"_MatriksIQ uygulamasının açık olduğunu doğrulayın._\n\n"
            f"{footer_block()}",
            parse_mode='Markdown'
        )


# ─────────────────────────────────────────────────────────────────────────────
#  SCANNER API KOMUTLARI (KAP, Radar, Teknik, AKD, Takas)
# ─────────────────────────────────────────────────────────────────────────────
def _run_scanner(cmd: str, symbol: str | None = None) -> list:
    """scanner_api.py fonksiyonlarını thread içinde çalıştır."""
    import importlib
    try:
        mod = importlib.import_module("api.scanner_api")
        fn_map = {
            "RADAR":  "get_radar_tarama",
            "TEKNIK": "get_teknik_tarama",
            "AKD":    "get_akd_tarama",
            "TAKAS":  "get_takas_tarama",
            "KAP":    "get_kap_ajan",
            "SINGLE": "calculate_single_indicators",
        }
        fn = getattr(mod, fn_map[cmd])
        if cmd in ("KAP", "SINGLE") and symbol:
            return fn(symbol)
        return fn()
    except Exception as e:
        logger.error(f"Scanner [{cmd}] hatası: {e}")
        return []


async def run_in_thread(cmd, symbol=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, _run_scanner, cmd, symbol)


# ─── /radar ───────────────────────────────────────────────────────────────────
async def cmd_radar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"{header('radar', 'Hisse Radar')}\n\n"
        f"{I['load']}  BIST taranıyor, fırsatlar hesaplanıyor...\n\n{footer_block()}",
        parse_mode='Markdown'
    )
    data = await run_in_thread("RADAR")
    if not data:
        await msg.edit_text(f"{header('err', 'Hisse Radar')}\n\n{I['err']}  Veri alınamadı.\n\n{footer_block()}", parse_mode='Markdown')
        return

    lines = [f"{header('radar', 'Hisse Radar — Günün Fırsatları')}\n"]
    for i, r in enumerate(data, 1):
        arrow = I['up'] if r.get('yon', '') == 'ALIŞ' else I['neutral']
        lines.append(
            f"{arrow}  *{r.get('symbol','?')}*  —  {r.get('title','')}\n"
            f"    {I['bullet']}  {r.get('detay','')}\n"
            f"    {I['bullet']}  Fiyat: `{r.get('value','?')}`"
        )

    lines.append(f"\n{footer_block()}")
    await msg.edit_text("\n\n".join(lines), parse_mode='Markdown')


# ─── /teknik ──────────────────────────────────────────────────────────────────
async def cmd_teknik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else None
    label  = f"Teknik Tarama{' — ' + symbol if symbol else ''}"
    msg = await update.message.reply_text(
        f"{header('teknik', label)}\n\n{I['load']}  İndikatörler hesaplanıyor...\n\n{footer_block()}",
        parse_mode='Markdown'
    )

    data = await run_in_thread("SINGLE", symbol) if symbol else await run_in_thread("TEKNIK")

    if isinstance(data, dict) and "rsi" in data:
        # Tekil hisse analizi
        price = data.get('price', 0)
        lines = [
            f"{header('teknik', f'Teknik Analiz — {symbol}')}\n",
            f"{I['ok']}  Fiyat            :  `{price:,.2f} ₺`",
            f"{I['ok']}  RSI (14)         :  `{data.get('rsi','?')}`",
            f"{I['ok']}  MACD             :  `{data.get('macd','?')}`",
            f"{I['ok']}  Hareketli Ort.   :  `{data.get('moving_averages','?')}`",
            f"\n{footer_block()}"
        ]
        await msg.edit_text("\n".join(lines), parse_mode='Markdown')
        return

    if not data:
        await msg.edit_text(f"{header('err', label)}\n\n{I['err']}  Veri alınamadı.\n\n{footer_block()}", parse_mode='Markdown')
        return

    lines = [f"{header('teknik', 'Teknik Tarama — BIST Özeti')}\n"]
    for r in data[:10]:
        rsi_val = float(r.get('rsi', 50))
        arrow = I['up'] if rsi_val < 45 else (I['down'] if rsi_val > 65 else I['neutral'])
        lines.append(
            f"{arrow}  *{r.get('symbol','?')}*  —  {r.get('status','')}\n"
            f"    {I['bullet']}  RSI: `{r.get('rsi','?')}`   Hacim: `{r.get('volume','?')}`   Fiyat: `{r.get('price','?')}`"
        )
    lines.append(f"\n{footer_block()}")
    await msg.edit_text("\n\n".join(lines), parse_mode='Markdown')


# ─── /akdtara ─────────────────────────────────────────────────────────────────
async def cmd_akdtara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"{header('akd', 'AKD Tarama')}\n\n{I['load']}  Kurum akışları analiz ediliyor...\n\n{footer_block()}",
        parse_mode='Markdown'
    )
    data = await run_in_thread("AKD")
    if not data:
        await msg.edit_text(f"{header('err', 'AKD Tarama')}\n\n{I['err']}  Veri alınamadı.\n\n{footer_block()}", parse_mode='Markdown')
        return

    lines = [f"{header('akd', 'AKD Tarama — Kurum Alım/Satım')}\n"]
    for r in data:
        arrow = I['up'] if r.get('yon', '') == 'ALIŞ' else I['down']
        lines.append(
            f"{arrow}  *{r.get('symbol','?')}*  —  {r.get('kurum','?')}\n"
            f"    {I['bullet']}  Yön: `{r.get('yon','?')}`   Hacim: `{r.get('net_hacim','?')}`"
        )
    lines.append(f"\n{footer_block()}")
    await msg.edit_text("\n\n".join(lines), parse_mode='Markdown')


# ─── /takastara ───────────────────────────────────────────────────────────────
async def cmd_takastara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text(
        f"{header('takas', 'Takas Tarama')}\n\n{I['load']}  MKK Saklama verileri inceleniyor...\n\n{footer_block()}",
        parse_mode='Markdown'
    )
    data = await run_in_thread("TAKAS")
    if not data:
        await msg.edit_text(f"{header('err', 'Takas Tarama')}\n\n{I['err']}  Veri alınamadı.\n\n{footer_block()}", parse_mode='Markdown')
        return

    lines = [f"{header('takas', 'Takas Tarama — MKK Saklama Özeti')}\n"]
    for r in data:
        lines.append(
            f"{I['neutral']}  *{r.get('symbol','?')}*  —  {r.get('kurum','?')}\n"
            f"    {I['bullet']}  Pay: `{r.get('yon','?')}`   Toplam Lot: `{r.get('net_hacim','?')}`"
        )
    lines.append(f"\n{footer_block()}")
    await msg.edit_text("\n\n".join(lines), parse_mode='Markdown')


# ─── /kap ─────────────────────────────────────────────────────────────────────
async def cmd_kap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    symbol = context.args[0].upper() if context.args else None
    label  = f"KAP Ajan{' — ' + symbol if symbol else ''}"
    msg = await update.message.reply_text(
        f"{header('kap', label)}\n\n{I['load']}  KAP bildirimleri alınıyor...\n\n{footer_block()}",
        parse_mode='Markdown'
    )
    data = await run_in_thread("KAP", symbol)
    if not data:
        await msg.edit_text(f"{header('err', label)}\n\n{I['err']}  Veri alınamadı.\n\n{footer_block()}", parse_mode='Markdown')
        return

    lines = [f"{header('kap', 'KAP Ajan — Son Bildirimler')}\n"]
    for r in data[:12]:
        urgent_icon = I['alert'] if r.get('urgent') else I['bullet']
        lines.append(
            f"{urgent_icon}  `[{r.get('time','--:--')}]`  *{r.get('source','KAP')}*\n"
            f"    {r.get('title','')[:100]}"
        )
    lines.append(f"\n{footer_block()}")
    await msg.edit_text("\n\n".join(lines), parse_mode='Markdown')


# ─────────────────────────────────────────────────────────────────────────────
#  /start — Ana Menü
# ─────────────────────────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"*{BRAND}*\n"
        f"{I['terminal']}  {TAGLINE}\n"
        f"{DIVIDER}\n\n"
        f"*{I['radar']}  VERİ TERMİNALİ*\n\n"
        f"  {I['radar']}  `/radar`       — Hisse Radar — Günün Fırsatları\n"
        f"  {I['teknik']}  `/teknik`      — Teknik Tarama  _(veya: `/teknik THYAO`)_\n"
        f"  {I['akd']}  `/akdtara`     — AKD Tarama — Kurum Alım/Satım\n"
        f"  {I['takas']}  `/takastara`   — Takas Tarama — MKK Saklama\n"
        f"  {I['kap']}  `/kap`         — KAP Ajan  _(veya: `/kap THYAO`)_\n\n"
        f"{DIVIDER}\n\n"
        f"*{I['depth']}  MATRİKS CANLI TERMİNAL*\n\n"
        f"  {I['depth']}  `/derinlik`    — 25 Kademe Derinlik\n"
        f"  {I['akd']}  `/akd`         — Araçı Kurum Dağılımı\n"
        f"  {I['takas']}  `/takas`       — Takas Verileri\n"
        f"  {I['bullet']}  `/islem`       — Zaman ve Satış\n"
        f"  {I['bullet']}  `/teorik`      — Teorik Eşleşme\n"
        f"  {I['chart']}  `/grafik`      — Teknik Grafik\n\n"
        f"  _{I['bullet']}  Kullanım: `/derinlik THYAO` — `/akd GARAN`_\n\n"
        f"{DIVIDER}\n"
        f"_{FOOTER}_"
    )
    await update.message.reply_text(text, parse_mode='Markdown')


# ─── Matriks Komut Handler'ları ───────────────────────────────────────────────
async def derinlik(u, c): await matriks_command(u, c, "f1",   "Kademe Analizi",       "Kademe Derinlik",      "depth")
async def akd     (u, c): await matriks_command(u, c, "f3",   "AracıKurumDagilimi",   "Araçı Kurum Dağılımı", "akd")
async def takas   (u, c): await matriks_command(u, c, "f4",   "Takas",                "Takas Verileri",       "takas")
async def islem   (u, c): await matriks_command(u, c, "f5",   "ZamanSatis",           "Zaman ve Satış",       "bullet")
async def teorik  (u, c): await matriks_command(u, c, "f8",   "TeorikEslesme",        "Teorik Eşleşme",       "neutral")
async def grafik  (u, c): await matriks_command(u, c, "altg", "Grafik",               "Teknik Grafik",        "chart")


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        logger.critical("TELEGRAM_BOT_TOKEN bulunamadı! .env dosyasını kontrol edin.")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()

    # ─── Handler kaydı ────────────────────────────────────────────────────────
    handlers = [
        ("start",      start),
        # Veri Terminali
        ("radar",      cmd_radar),
        ("teknik",     cmd_teknik),
        ("akdtara",    cmd_akdtara),
        ("takastara",  cmd_takastara),
        ("kap",        cmd_kap),
        # Matriks Live
        ("derinlik",   derinlik),
        ("akd",        akd),
        ("takas",      takas),
        ("islem",      islem),
        ("teorik",     teorik),
        ("grafik",     grafik),
    ]
    for name, fn in handlers:
        app.add_handler(CommandHandler(name, fn))

    # ─── Bot komut menüsü ─────────────────────────────────────────────────────
    commands = [
        BotCommand("start",      "Paribu Menkul Değer — Ana Menü"),
        BotCommand("radar",      "Hisse Radar — Günlük Fırsatlar"),
        BotCommand("teknik",     "Teknik Tarama (ör: /teknik THYAO)"),
        BotCommand("akdtara",    "AKD Tarama — Kurum Alım/Satım"),
        BotCommand("takastara",  "Takas Tarama — MKK Saklama"),
        BotCommand("kap",        "KAP Ajan - Son Bildirimler"),
        BotCommand("derinlik",   "MatriksIQ — 25 Kademe Derinlik"),
        BotCommand("akd",        "MatriksIQ — Araçı Kurum Dağılımı"),
        BotCommand("takas",      "MatriksIQ — Takas Verileri"),
        BotCommand("islem",      "MatriksIQ — Zaman ve Satış"),
        BotCommand("teorik",     "MatriksIQ — Teorik Eşleşme"),
        BotCommand("grafik",     "MatriksIQ — Teknik Grafik"),
    ]

    async def post_init(application):
        await application.bot.set_my_commands(commands)
        logger.info(f"{BRAND} — Aktif. {len(handlers)} komut yüklendi.")

    app.post_init = post_init

    print(f"\n{DIVIDER}")
    print(f"  {BRAND}")
    print(f"  {TAGLINE}")
    print(f"{DIVIDER}")
    print(f"  {I['ok']} {len(handlers)} komut yüklendi ve bağlantı bekleniyor...")
    print(f"{DIVIDER}\n")

    app.run_polling(drop_pending_updates=True)
