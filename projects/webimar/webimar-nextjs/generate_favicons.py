#!/usr/bin/env python3
"""
Tarım İmar Favicon Generator
SEO uyumlu favicon dosyaları oluşturur
"""

import os
import json
from pathlib import Path

class FaviconGenerator:
    def __init__(self, public_dir):
        self.public_dir = Path(public_dir)
        self.sizes = {
            'favicon-16x16.svg': 16,
            'favicon-32x32.svg': 32,
            'favicon.svg': 32,
            'apple-touch-icon.svg': 180
        }

    def create_svg_favicon(self, filename, emoji, size):
        """SVG favicon oluştur"""
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <style>
      .emoji {{
        font-size: {size * 0.75}px;
        text-anchor: middle;
        dominant-baseline: middle;
      }}
    </style>
  </defs>
  <rect width="{size}" height="{size}" fill="#D2691E" rx="{size * 0.2}"/>
  <text x="{size/2}" y="{size/2}" class="emoji">{emoji}</text>
</svg>'''

        filepath = self.public_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✅ {filename} oluşturuldu")

    def create_manifest(self):
        """Web App Manifest oluştur"""
        manifest = {
            "name": "Tarım İmar - Tarımsal Yapılaşma Hesaplama",
            "short_name": "Tarım İmar",
            "description": "Tarımsal arazilerde yapılaşma hesaplamaları",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#D2691E",
            "theme_color": "#D2691E",
            "icons": [
                {
                    "src": "/favicon-16x16.svg",
                    "sizes": "16x16",
                    "type": "image/svg+xml"
                },
                {
                    "src": "/favicon-32x32.svg",
                    "sizes": "32x32",
                    "type": "image/svg+xml"
                },
                {
                    "src": "/apple-touch-icon.svg",
                    "sizes": "180x180",
                    "type": "image/svg+xml"
                }
            ]
        }

        manifest_path = self.public_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print("✅ manifest.json güncellendi")

    def create_robots_txt(self):
        """SEO uyumlu robots.txt oluştur"""
        robots_content = """User-agent: *
Allow: /

# Sitemap
Sitemap: https://tarimimar.com.tr/sitemap.xml

# Block access to sensitive files
Disallow: /api/
Disallow: /admin/
Disallow: /_next/
Disallow: /static/
"""

        robots_path = self.public_dir / "robots.txt"
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots_content)
        print("✅ robots.txt güncellendi")

    def generate_all(self):
        """Tüm favicon dosyalarını oluştur"""
        print("🚀 Tarım İmar Favicon Generator başlatılıyor...")

        # Temizleme
        self.cleanup_old_files()

        # SVG favicon'lar oluştur
        self.create_svg_favicon('favicon.svg', '🏗️', 32)  # Google aramaları için
        self.create_svg_favicon('favicon-16x16.svg', '🌾', 16)  # Tarayıcı sekmesi için
        self.create_svg_favicon('favicon-32x32.svg', '🏗️', 32)  # Yedek
        self.create_svg_favicon('apple-touch-icon.svg', '🏗️', 180)  # iOS için

        # SEO dosyaları
        self.create_manifest()
        self.create_robots_txt()

        print("✅ Tüm favicon dosyaları başarıyla oluşturuldu!")
        print("📝 favicon.ico için manuel güncelleme gerekebilir")

    def cleanup_old_files(self):
        """Eski gereksiz dosyaları temizle"""
        old_files = [
            'favicon-design-instructions.txt',
            'FAVICON_UPDATE_INSTRUCTIONS.txt'
        ]

        for filename in old_files:
            filepath = self.public_dir / filename
            if filepath.exists():
                filepath.unlink()
                print(f"🗑️  {filename} silindi")

def main():
    # Public dizini belirle
    script_dir = Path(__file__).parent
    public_dir = script_dir / "public"

    if not public_dir.exists():
        print(f"❌ Public dizini bulunamadı: {public_dir}")
        return

    # Generator oluştur ve çalıştır
    generator = FaviconGenerator(public_dir)
    generator.generate_all()

if __name__ == "__main__":
    main()
