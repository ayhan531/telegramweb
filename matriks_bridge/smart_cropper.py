from PIL import Image
import os

def find_and_crop_window(input_img="matriks_full_state.png", output_img="cropped_result.png"):
    """
    Matriks full ekran görüntüsü içinde mavi başlık çubuğuna (title bar) sahip 
    iç pencereyi bulur ve kırpar.
    """
    if not os.path.exists(input_img):
        print("Giriş dosyası bulunamadı.")
        return False
        
    img = Image.open(input_img).convert("RGB")
    w, h = img.size
    pixels = img.load()
    
    # Matriks IQ iç pencere başlık rengi (Koyu Mavi - Yaklaşık)
    # Fotoğraftan alınan örnek: (0, 75, 137) civarı
    TARGET_COLOR = (0, 120, 215) 
    TOLERANCE = 40
    
    def is_blue(p):
        return abs(p[0] - 0) < TOLERANCE and abs(p[1] - 120) < TOLERANCE and abs(p[2] - 215) < TOLERANCE

    # Pencerenin üst-sol ve alt-sağ köşelerini bulalım
    found_top = None
    
    # Üstten aşağı, soldan sağa tara
    # %15 içeriden başla (Sol paneli atla)
    for y in range(int(h * 0.05), int(h * 0.8)):
        for x in range(int(w * 0.15), int(w * 0.8)):
            if is_blue(pixels[x, y]):
                # Bu bir başlık çubuğu başlangıcı olabilir mi? 
                # Sağındakiler de mavi mi kontrol et (En az 300 piksel genişlik)
                if x + 300 < w and all(is_blue(pixels[x+i, y]) for i in range(300)):
                    found_top = (x, y)
                    break
        if found_top: break
        
    if not found_top:
        print("⚠️ İç pencere başlığı bulunamadı.")
        return False
    
    # Pencerenin genişliğini ve yüksekliğini saptayalım
    # Genişlik: Mavi çizgi nerede bitiyor?
    curr_x = found_top[0]
    while curr_x < w - 5 and is_blue(pixels[curr_x, found_top[1]]):
        curr_x += 1
    p_width = curr_x - found_top[0]
    
    # Yükseklik: Tahmini veya alt kenar arayarak
    # Matriks pencereleri genelde benzer oranlardadır veya alt gri sınırı vardır.
    # Şimdilik Takas/Derinlik için ortalama bir yükseklik veya dikey çizgi bitimi bakabiliriz.
    curr_y = found_top[1]
    # Başlık çubuğu genelde 25-30 pikseldir. Ondan sonra içerik başlar.
    # Pencerenin bittiği yeri (alttaki çerçeveyi) bulmaya çalışalım
    # Veya sabit bir oranla gidelim (Hız için)
    # Takas penceresi fotoğrafta oldukça büyük.
    
    # Alternatif: Pencerenin sağ sınırından aşağı inip gri/mavi köşeyi bul
    # Ama şimdilik basitçe dikeyde %80'ini alıyoruz (Gerekirse ayarlanır)
    p_height = int(h * 0.8) # Varsayılan yüksek bir değer
    
    # Kırp ve kaydet
    # (left, top, right, bottom)
    # Hafif çerçeve payları için ayarlama yapabiliriz
    box = (found_top[0]-5, found_top[1]-5, found_top[0] + p_width + 5, found_top[1] + p_height)
    cropped = img.crop(box)
    cropped.save(output_img)
    print(f"✅ Kırpma başarılı! {output_name if 'output_name' in locals() else output_img}")
    return True

if __name__ == "__main__":
    find_and_crop_window()
