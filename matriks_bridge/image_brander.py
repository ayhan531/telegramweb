"""
Gelen fotoğrafı kişiselleştiren modül.
- Hedef botun watermark/link alanlarını siler (üstüne kapatır)
- Kendi markamızı (başlık + alt bilgi) ekler
- Orijinal fotoğraftaki renk paletini korur
"""

from PIL import Image, ImageDraw, ImageFont
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


def brand_image(raw_bytes: bytes, symbol: str = "", data_type: str = "AKD") -> bytes:
    """
    Parametre olarak aldığı ham JPEG/PNG byte'larını işler:
    1. Hedef botun watermark/link satırlarını kapatır
    2. Kendi başlık ve alt bilgimizi ekler
    3. Sonucu JPEG byte dizisi olarak döndürür
    """
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # ── Fontları yükle ──────────────────────────────────────────
    font_title  = _load_font(max(13, w // 32))
    font_sub    = _load_font(max(10, w // 44))
    font_brand  = _load_font(max(11, w // 38))

    # ── 1) Kaynak botu gizle: üstteki watermark bölgesini kapat ──
    # Hedef botun fotoğrafında üst bölümde sembol ismi, link ve kaynak bilgisi bulunur.
    # Tamamını bir dikdörtgenle örteceğiz.
    cover_top_h = int(h * 0.22)   # üst %22'yi kapat (kaynak bot metni)
    draw.rectangle([(0, 0), (w, cover_top_h)], fill=COVER_COLOR)

    # ── 2) Kendi başlık çubuğumuzu ekle ─────────────────────────────
    bar_h = int(h * 0.13)
    draw.rectangle([(0, 0), (w, bar_h)], fill=BRAND_BG)

    # Sol: Sembol adı + veri tipi
    if symbol:
        title_text = f"{symbol}  —  {data_type.upper()}"
        draw.text((16, 8), title_text, font=font_title, fill=BRAND_COLOR)

    # Sağ: Marka adı
    brand_bbox = draw.textbbox((0, 0), BRAND_NAME, font=font_brand)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text((w - brand_w - 16, 8), BRAND_NAME, font=font_brand, fill=BRAND_TEXT_CLR)

    # ── 3) Sol dikey şerit (ince çizgi) ─────────────────────────
    draw.rectangle([(0, 0), (3, h)], fill=BRAND_COLOR)

    # ── 4) Alt bilgi çubuğu ─────────────────────────────────────
    footer_h = int(h * 0.07)
    draw.rectangle([(0, h - footer_h), (w, h)], fill=BRAND_BG)

    # Alt: copyright
    sub_bbox = draw.textbbox((0, 0), BRAND_SUBTITLE, font=font_sub)
    sub_w = sub_bbox[2] - sub_bbox[0]
    sub_y = h - footer_h + (footer_h - (sub_bbox[3] - sub_bbox[1])) // 2
    draw.text(((w - sub_w) // 2, sub_y), BRAND_SUBTITLE, font=font_sub, fill=(140, 140, 150))

    # ── 5) Çıkış: JPEG olarak sıkıştır ──────────────────────────
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=92)
    out.seek(0)
    return out.read()
