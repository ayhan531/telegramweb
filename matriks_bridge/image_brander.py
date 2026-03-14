from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import io
import os

# ── Marka Ayarları ──────────────────────────────────────────────
BRAND_NAME      = "ANALYTICAL DATA TERMINAL"
BRAND_SUBTITLE  = "© 2026  •  Tüm Hakları Saklıdır"
BRAND_COLOR     = (0, 212, 255)       # Cyan — premium his
BRAND_BG        = (10, 10, 14)        # Neredeyse siyah arka plan
BRAND_TEXT_CLR  = (220, 220, 220)     # Açık gri metin

# Watermark kaplama rengi (orijinal arka planla uyumlu koyu renk)
COVER_COLOR     = (10, 10, 14)

# ── Font yükleme ─────────────────────────────────────────────────
def _load_font(size: int):
    """Sistem fontlarından uygun birini yükler."""
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _clean_watermark(img: Image.Image) -> Image.Image:
    """
    Arka plandaki sinsi gri logoları temizler.
    """
    img = img.convert("RGB")
    data = img.getdata()
    new_data = []
    bg_color = (10, 10, 14)
    threshold = 110 # Daha hassas eşik
    
    for item in data:
        # Renklerin sönüklüğünü kontrol et
        if (item[0] + item[1] + item[2]) // 3 < threshold:
            new_data.append(bg_color)
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    return img

def brand_image(raw_bytes: bytes, symbol: str = "", data_type: str = "AKD") -> bytes:
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    
    # ── 1) Kalite Arttırımı (Upscale & Enhancement) ──
    # Canlılık için renkleri %40 arttır
    img = ImageEnhance.Color(img).enhance(1.4)
    # Kontrastı %20 arttır
    img = ImageEnhance.Contrast(img).enhance(1.2)
    
    # Arka plan temizliği
    img = _clean_watermark(img)
    
    # 2 kat büyüt (Fontların daha net çıkması için)
    w_orig, h_orig = img.size
    img = img.resize((w_orig * 2, h_orig * 2), Image.Resampling.LANCZOS)
    
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # ── Fontları yükle (Büyük boyuta göre) ──
    font_title  = _load_font(max(26, w // 28))
    font_sub    = _load_font(max(20, w // 40))
    font_brand  = _load_font(max(22, w // 34))

    # ── 2) Kaynak botu gizle ──
    # Üst Bölgeyi kapat
    draw.rectangle([(0, 0), (w, int(h * 0.20))], fill=COVER_COLOR)
    # Alt Bölgeyi kapat
    draw.rectangle([(0, int(h * 0.94)), (w, h)], fill=COVER_COLOR)

    # ── 3) Kendi başlık çubuğumuzu ekle ──
    bar_h = int(h * 0.12)
    draw.rectangle([(0, 0), (w, bar_h)], fill=BRAND_BG)

    # Sol: Sembol adı + veri tipi
    if symbol:
        title_text = f"{symbol}  —  {data_type.upper()}"
        draw.text((32, 20), title_text, font=font_title, fill=BRAND_COLOR)

    # Sağ: Marka adı
    brand_bbox = draw.textbbox((0, 0), BRAND_NAME, font=font_brand)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text((w - brand_w - 32, 22), BRAND_NAME, font=font_brand, fill=BRAND_TEXT_CLR)

    # ── 4) Sol dikey şerit ──
    draw.rectangle([(0, 0), (8, h)], fill=BRAND_COLOR)

    # ── 5) Alt bilgi çubuğu ──
    footer_h = int(h * 0.06)
    draw.rectangle([(0, h - footer_h), (w, h)], fill=BRAND_BG)

    # Alt: copyright
    sub_bbox = draw.textbbox((0, 0), BRAND_SUBTITLE, font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_y = h - footer_h + (footer_h - (sub_bbox[3] - sub_bbox[1])) // 2
    draw.text(((w - sub_w) // 2, sub_y), BRAND_SUBTITLE, font=font_sub, fill=(140, 140, 150))

    # Keskinliği arttır (Son dokunuş)
    img = ImageEnhance.Sharpness(img).enhance(1.5)

    # ── 6) Çıkış: Yüksek Kaliteli JPEG ──
    out = io.BytesIO()
    # subsampling=0 (4:4:4) ile renk bozulmalarını engelle
    img.save(out, format="JPEG", quality=98, subsampling=0)
    out.seek(0)
    return out.read()

