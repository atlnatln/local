#!/usr/bin/env python3
"""
Tarım İmar ICO Favicon Generator
favicon.ico dosyasını otomatik olarak oluşturur
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_ico_favicon(emoji="🏗️", output_path="public/favicon.ico"):
    """ICO favicon oluştur"""
    # 32x32 boyutunda şeffaf arka plan
    size = 32
    image = Image.new('RGBA', (size, size), (210, 105, 30, 255))  # D2691E rengi
    draw = ImageDraw.Draw(image)

    # Emoji için font ayarı (sistem fontu kullan)
    try:
        # Linux sistemlerde emoji fontu
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size-8)
    except:
        try:
            # Alternatif font
            font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size-8)
        except:
            # Fallback
            font = ImageFont.load_default()

    # Emoji'yi merkeze yerleştir
    bbox = draw.textbbox((0, 0), emoji, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Emoji'yi çiz
    draw.text((x, y), emoji, fill=(255, 255, 255, 255), font=font)

    # ICO olarak kaydet
    image.save(output_path, format='ICO', sizes=[(32, 32), (16, 16)])
    print(f"✅ {output_path} oluşturuldu ({size}x{size})")

def main():
    script_dir = Path(__file__).parent
    output_path = script_dir / "public" / "favicon.ico"

    # Eski favicon.ico varsa yedekle
    if output_path.exists():
        backup_path = output_path.with_suffix('.ico.backup')
        output_path.rename(backup_path)
        print(f"📦 Eski favicon.ico yedeklendi: {backup_path}")

    # Yeni favicon.ico oluştur
    create_ico_favicon("🏗️", output_path)

    print("🎉 favicon.ico başarıyla oluşturuldu!")
    print("🔍 Google aramalarında 🏗️, tarayıcı sekmesinde 🌾 görünecek")

if __name__ == "__main__":
    main()
