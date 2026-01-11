# sitemap.xml Otomatik Oluşturucu

from django.core.management.base import BaseCommand
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import xml.etree.ElementTree as ET
import os
import requests
from typing import List, Dict

class Command(BaseCommand):
    help = 'Generate sitemap.xml with only live pages (GSC indexing fix)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-urls',
            action='store_true',
            help='Check if URLs are accessible before adding to sitemap',
        )
        parser.add_argument(
            '--notify-google',
            action='store_true', 
            help='Notify Google after sitemap generation',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Generating sitemap.xml...')
        
        # Collect all valid URLs
        urls = self.collect_urls()
        
        # Filter URLs if --check-urls flag is provided
        if options.get('check_urls'):
            self.stdout.write('🔍 Checking URL accessibility...')
            urls = self.filter_accessible_urls(urls)
        
        # Generate XML
        sitemap_content = self.generate_sitemap_xml(urls)
        
        # Save to static directory
        output_path = os.path.join(settings.STATIC_ROOT or 'static', 'sitemap.xml')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sitemap_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Sitemap generated with {len(urls)} URLs: {output_path}')
        )
        
        # Notify Google if requested
        if options.get('notify_google'):
            self.notify_search_engines(output_path)

    def collect_urls(self) -> List[Dict]:
        """Collect all valid URLs for sitemap"""
        base_url = 'https://tarimimar.com.tr'
        urls = []
        now = timezone.now()
        
        # Ana sayfa
        urls.append({
            'loc': f'{base_url}/',
            'lastmod': now.isoformat(),
            'changefreq': 'weekly',
            'priority': '1.0'
        })
        
        # Yapı türü sayfaları (Next.js landing pages)
        structure_types = [
            'sera', 'bag-evi', 'mantar-tesisi', 'hububat-silo', 'tarimsal-depo',
            'lisansli-depo', 'yikama-tesisi', 'kurutma-tesisi', 'meyve-sebze-kurutma',
            'zeytinyagi-fabrikasi', 'su-depolama', 'su-kuyulari', 'zeytinyagi-uretim-tesisi',
            'soguk-hava-deposu', 'sut-sigirciligi', 'agil-kucukbas', 'kumes-yumurtaci',
            'kumes-etci', 'kumes-gezen', 'kumes-hindi', 'kaz-ordek', 'hara',
            'ipek-bocekciligi', 'evcil-hayvan', 'besi-sigirciligi', 'solucan-tesisi', 'aricilik'
        ]
        
        for structure_type in structure_types:
            urls.append({
                'loc': f'{base_url}/{structure_type}/',
                'lastmod': now.isoformat(),
                'changefreq': 'monthly',
                'priority': '0.8'
            })
        
        # Hesaplama araçları (Next.js özel sayfalar)
        special_pages = [
            'sigir-ahiri-kapasite-hesaplama',
            'gubre-cukuru-hesaplama',
            'aricilik-planlama',
            'ciceklenme-takvimi'
        ]
        
        for page in special_pages:
            urls.append({
                'loc': f'{base_url}/{page}/',
                'lastmod': now.isoformat(),
                'changefreq': 'monthly',
                'priority': '0.9'
            })
        
        # Document pages
        document_pages = [
            'documents/izmir-buyuksehir-plan-notlari',
            'documents/tarim-arazileri-kullanimi-genelgesi'
        ]
        
        for doc in document_pages:
            urls.append({
                'loc': f'{base_url}/{doc}/',
                'lastmod': now.isoformat(),
                'changefreq': 'yearly',
                'priority': '0.6'
            })
        
        # Static pages
        static_pages = [
            'gizlilik-politikasi',
            'kullanim-kosullari', 
            'cerez-politikasi',
            'kvkk-aydinlatma'
        ]
        
        for page in static_pages:
            urls.append({
                'loc': f'{base_url}/{page}/',
                'lastmod': now.isoformat(),
                'changefreq': 'yearly',
                'priority': '0.3'
            })
        
        self.stdout.write(f'📝 Collected {len(urls)} URLs')
        return urls

    def filter_accessible_urls(self, urls: List[Dict]) -> List[Dict]:
        """Filter out URLs that return 404 or 5xx errors"""
        accessible_urls = []
        
        for url_info in urls:
            try:
                response = requests.head(
                    url_info['loc'], 
                    timeout=10,
                    allow_redirects=True,
                    headers={'User-Agent': 'Webimar Sitemap Generator'}
                )
                
                if response.status_code == 200:
                    accessible_urls.append(url_info)
                elif response.status_code in [301, 302]:
                    # Update URL to final redirect destination
                    final_url = response.url
                    url_info['loc'] = final_url
                    accessible_urls.append(url_info)
                    self.stdout.write(f'🔄 Redirect: {url_info["loc"]} → {final_url}')
                else:
                    self.stdout.write(
                        self.style.WARNING(f'❌ Skipping {url_info["loc"]} (HTTP {response.status_code})')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'❌ Skipping {url_info["loc"]} (Error: {str(e)})')
                )
        
        self.stdout.write(f'✅ {len(accessible_urls)}/{len(urls)} URLs are accessible')
        return accessible_urls

    def generate_sitemap_xml(self, urls: List[Dict]) -> str:
        """Generate XML sitemap content"""
        
        # Create root element
        urlset = ET.Element(
            'urlset',
            xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'
        )
        
        # Add each URL
        for url_info in urls:
            url_elem = ET.SubElement(urlset, 'url')
            
            # Required elements
            ET.SubElement(url_elem, 'loc').text = url_info['loc']
            ET.SubElement(url_elem, 'lastmod').text = url_info['lastmod']
            
            # Optional elements
            if 'changefreq' in url_info:
                ET.SubElement(url_elem, 'changefreq').text = url_info['changefreq']
            if 'priority' in url_info:
                ET.SubElement(url_elem, 'priority').text = str(url_info['priority'])
        
        # Convert to string with XML declaration
        xml_str = ET.tostring(urlset, encoding='utf-8', xml_declaration=True)
        
        # Pretty print (optional, for readability)
        try:
            import xml.dom.minidom
            dom = xml.dom.minidom.parseString(xml_str)
            return dom.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
        except:
            # Fallback to non-pretty printed version
            return xml_str.decode('utf-8')

    def notify_search_engines(self, sitemap_path: str):
        """Notify Google and Bing about sitemap updates"""
        base_url = 'https://tarimimar.com.tr'
        sitemap_url = f'{base_url}/static/sitemap.xml'
        
        # Google
        google_ping_url = f'https://www.google.com/ping?sitemap={sitemap_url}'
        try:
            response = requests.get(google_ping_url, timeout=10)
            if response.status_code == 200:
                self.stdout.write('📧 Google notified successfully')
            else:
                self.stdout.write(f'⚠️ Google notification failed: HTTP {response.status_code}')
        except Exception as e:
            self.stdout.write(f'⚠️ Google notification error: {str(e)}')
        
        # Bing
        bing_ping_url = f'https://www.bing.com/ping?sitemap={sitemap_url}'
        try:
            response = requests.get(bing_ping_url, timeout=10)
            if response.status_code == 200:
                self.stdout.write('📧 Bing notified successfully')
            else:
                self.stdout.write(f'⚠️ Bing notification failed: HTTP {response.status_code}')
        except Exception as e:
            self.stdout.write(f'⚠️ Bing notification error: {str(e)}')