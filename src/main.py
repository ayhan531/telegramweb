import logging
import os
import matplotlib.pyplot as plt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import load_dotenv
from api.tv_api import get_tv_stock_data, get_tv_stock_history
from api.real_akd_api import get_real_akd_data
from utils.chart_generator import create_stock_chart

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "FINANSAL ANALIZ SISTEMI\n"
        "-----------------------------------\n"
        "BIST veri terminaline hos geldiniz.\n\n"
        "KOMUTLAR\n"
        "/derinlik [SEMBOL] - Piyasa verileri\n"
        "/grafik [SEMBOL]   - Teknik analiz grafigi\n"
        "/yardim           - Detayli dokumantasyon"
    )
    
    keyboard = [
        [InlineKeyboardButton("VERI TERMINALINI AC", web_app=WebAppInfo(url="https://telegramweb-gd62.onrender.com"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"```\n{welcome_text}\n```", 
        parse_mode='MarkdownV2',
        reply_markup=reply_markup
    )

async def yardim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "KULLANIM REHBERI\n"
        "-----------------------------------\n"
        "Veri sorgulamak için sembol kodunu komutla birlikte giriniz.\n\n"
        "ÖRNEKLER\n"
        "/derinlik THYAO\n"
        "/grafik EREGL\n\n"
        "NOT: Veriler 15 dakika gecikmelidir."
    )
    await update.message.reply_text(f"```\n{help_text}\n```", parse_mode='MarkdownV2')

async def derinlik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("HATA: Sembol girilmedi.")
        return
    
    symbol = context.args[0].upper()
    data = get_tv_stock_data(symbol)
    
    if not data:
        await update.message.reply_text(f"HATA: {symbol} verisi bulunamadi.")
        return
        
    # Profesyonel tablo görünümü
    text = (
        f"PIYASA VERISI: {symbol}\n"
        f"{'-' * 30}\n"
        f"{'Sirket:':<15} {data['name']}\n"
        f"{'Fiyat:':<15} {data['price']:.2f} {data['currency']}\n"
        f"{'Acilis:':<15} {data['open']:.2f}\n"
        f"{'Yuksek:':<15} {data['high']:.2f}\n"
        f"{'Dusuk:':<15} {data['low']:.2f}\n"
        f"{'Hacim:':<15} {data['volume']:,}\n"
        f"{'-' * 30}\n"
        f"Kaynak: TradingView (Anlik)"
    )
    await update.message.reply_text(f"```\n{text}\n```", parse_mode='MarkdownV2')

async def grafik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("HATA: Sembol girilmedi.")
        return
    
    symbol = context.args[0].upper()
    
    hist = get_tv_stock_history(symbol)
    if hist is None or hist.empty:
        await update.message.reply_text(f"HATA: {symbol} gecmis verisi bulunamadi.")
        return
        
    chart_path = f"{symbol}_chart.png"
    if create_stock_chart(hist, symbol, chart_path):
        caption = f"TEKNIK ANALIZ: {symbol}\nKaynak: TradingView"
        await update.message.reply_photo(photo=open(chart_path, 'rb'), caption=f"```\n{caption}\n```", parse_mode='MarkdownV2')
        os.remove(chart_path)
    else:
        await update.message.reply_text("HATA: Grafik olusturulamadi.")

async def akd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("HATA: Sembol girilmedi.")
        return
    
    symbol = context.args[0].upper()
    data = get_real_akd_data(symbol)
    
    if not data or not data['buyers']:
        await update.message.reply_text(f"HATA: {symbol} icin gercek AKD verisi su an alinamiye.")
        return
        
    # Profesyonel tablo görünümü
    text = f"GERCEK AKD VERISI: {symbol}\n"
    text += f"{'-' * 35}\n"
    text += f"{'ALICILAR':<20} {'LOT':>14}\n"
    for b in data['buyers']:
        text += f"{b['kurum'][:19]:<20} {b['lot']:>14}\n"
    
    text += f"\n{'SATICILAR':<20} {'LOT':>14}\n"
    for s in data['sellers']:
        text += f"{s['kurum'][:19]:<20} {s['lot']:>14}\n"
    
    text += f"{'-' * 35}\n"
    text += "Kaynak: Is Yatirim (Anlik)"
    
    await update.message.reply_text(f"```\n{text}\n```", parse_mode='MarkdownV2')

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_bot_token_here":
        print("Hata: TELEGRAM_BOT_TOKEN ayarlanmamış! Lütfen .env dosyasını güncelleyin.")
    else:
        application = ApplicationBuilder().token(token).build()
        
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('yardim', yardim))
        application.add_handler(CommandHandler('derinlik', derinlik))
        application.add_handler(CommandHandler('grafik', grafik))
        application.add_handler(CommandHandler('akd', akd))
        
        print("Bot başlatılıyor...")
        application.run_polling()
