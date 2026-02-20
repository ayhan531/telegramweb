import matplotlib.pyplot as plt
import pandas as pd
import os

def create_stock_chart(df, symbol, output_path):
    """Hisse senedi verilerini kullanarak profesyonel, temiz bir grafik oluşturur."""
    if df.empty:
        return False
    
    # Modern, profesyonel bir stil
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
    
    # Kapanış fiyatı çizimi
    ax.plot(df.index, df['Close'], color='#00d1b2', linewidth=2, label='Kapanis')
    
    # Dolgu (Area chart etkisi)
    ax.fill_between(df.index, df['Close'], color='#00d1b2', alpha=0.1)
    
    # Başlık ve Etiketler
    ax.set_title(f"FINANSAL ANALIZ: {symbol.upper()}", fontsize=14, fontweight='bold', pad=20, color='white')
    ax.set_xlabel("Zaman", fontsize=10, color='#888888')
    ax.set_ylabel(f"Fiyat", fontsize=10, color='#888888')
    
    # Grid ayarları
    ax.grid(True, linestyle='--', alpha=0.2, color='#ffffff')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444444')
    ax.spines['bottom'].set_color('#444444')
    
    plt.tight_layout()
    plt.savefig(output_path, facecolor='#121212', edgecolor='none')
    plt.close()
    return True
