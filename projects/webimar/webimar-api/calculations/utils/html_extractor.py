"""
HTML extraction & sanitization helper for calculation results.

Kısaca:
- extract_clean_html_from_result(result_obj) result objesinden (dict veya str) en anlamlı HTML snippet'i çıkarır
  (öncelik: sınıfında '-sonuc' veya 'sonuc' geçen element).
- BeautifulSoup ve bleach varsa kullanır. Yoksa regex fallback uygular.
"""
import re
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except Exception:
    BeautifulSoup = None  # type: ignore
    HAS_BS4 = False

try:
    import bleach
    HAS_BLEACH = True
except Exception:
    bleach = None  # type: ignore
    HAS_BLEACH = False

# Basit whitelist - CSS style'lar çıkarıldı (CSS sanitizer olmadan style attribute'ları güvenli değil)
ALLOWED_TAGS = [
    'div', 'span', 'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td',
    'h1', 'h2', 'h3', 'h4', 'p', 'b', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'hr',
    'pre', 'code', 'small'
]
ALLOWED_ATTRS = {
    '*': ['class', 'id', 'title'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height']
}

_CLASS_SONUC_RE = re.compile(r'(^|[\s"-])(.+?-sonuc$)|\bsonuc\b', re.IGNORECASE)

def _find_target_with_bs(soup) -> Optional[tuple]:
    """
    BeautifulSoup tabanlı çıkarıcı:
    - önce sınıfında '-sonuc' veya 'sonuc' içeren ilk elementi bulur.
    - bulunduysa aynı parent içinde bulunan <style> tag'larını da toplar ve (style_html, target_html) döner.
    - bulunamazsa style sonrası gelen next sibling'ı dener.
    - bulunamazsa ilk anlamlı div/section/article'ı bulur.
    """
    # 1) element sınıfıyla arama
    for tag in soup.find_all(True):
        classes = tag.get('class') or []
        for c in classes:
            if c and (c.lower().endswith('-sonuc') or 'sonuc' in c.lower()):
                # aynı parent'taki style tag'larını topla (örn. style + target birlikte gönderildiğinde)
                style_html = ''
                parent = tag.parent
                if parent:
                    for child in parent.children:
                        if getattr(child, 'name', None) == 'style':
                            style_html += str(child)
                        if child is tag:
                            break
                return style_html, str(tag)
    
    # 2) <style> sonrası gelen sibling
    style_tag = soup.find('style')
    if style_tag:
        next_el = style_tag.find_next_sibling()
        if next_el and getattr(next_el, 'text', '').strip():
            return str(style_tag), str(next_el)
    
    # 3) fallback: ilk büyük div/section/article
    for tag in soup.find_all(['div', 'section', 'article']):
        txt = tag.get_text(strip=True)
        if txt and len(txt) > 30:
            return '', str(tag)
    
    return None

def _sanitize_html(html: str) -> str:
    if not html:
        return ''
    
    if HAS_BLEACH:
        try:
            # önce script ve style içeriklerini tamamen çıkar
            # bleach bu tag'ların içeriklerini bırakabiliyor
            cleaned = re.sub(r'<script[\s\S]*?>[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
            cleaned = re.sub(r'<style[\s\S]*?>[\s\S]*?</style>', '', cleaned, flags=re.IGNORECASE)
            
            # bleach.clean ile whitelist uygula (CSS style'lar güvenlik için çıkarıldı)
            cleaned = bleach.clean(
                cleaned,
                tags=ALLOWED_TAGS,
                attributes=ALLOWED_ATTRS,
                strip=True  # tag'ları çıkar, içerikleri koru (ama script/style zaten çıkarıldı)
            )
            return cleaned
        except Exception:
            # bleach hatası durumunda basit fallback
            pass
    
    # Basit fallback: script'leri ve on* attributeları kaldır
    cleaned = re.sub(r'<script[\s\S]*?>[\s\S]*?</script>', '', html, flags=re.IGNORECASE)
    cleaned = re.sub(r'<style[\s\S]*?>[\s\S]*?</style>', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\son\w+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s>]+)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'href\s*=\s*["\']\s*javascript:[^"\']*["\']', 'href="#"', cleaned, flags=re.IGNORECASE)
    return cleaned

def _extract_by_regex(html: str) -> Optional[str]:
    """Basit regex fallback: ilk div/section/article içinde 'sonuc' sınıfı arar veya büyük bir div döner"""
    try:
        m = re.search(r'(<(?:div|section|article)[^>]*class=["\'][^"\']*(?:sonuc)[^"\']*["\'][\s\S]*?<\/(?:div|section|article)>)', html, flags=re.IGNORECASE)
        if m:
            return m.group(1)
        
        m2 = re.search(r'(<(?:div|section|article)[\s\S]{30,}?</(?:div|section|article)>)', html, flags=re.IGNORECASE)
        if m2:
            return m2.group(1)
    except Exception:
        return None
    
    return None

def extract_clean_html_from_result(result_obj: Any) -> str:
    """
    Public helper:
    - result_obj: dict veya string
    - dönen: sanitize edilmiş HTML snippet (string) — boş string dönebilir.
    """
    candidate_html = None
    
    if not result_obj:
        return ''
    
    if isinstance(result_obj, str):
        candidate_html = result_obj
    elif isinstance(result_obj, dict):
        # Öncelik sıralaması: result, html_mesaj, mesaj, ana_mesaj, detay_mesaji
        priority_keys = ['result', 'html_mesaj', 'mesaj', 'ana_mesaj', 'detay_mesaji']
        
        for k in priority_keys:
            v = result_obj.get(k)
            if isinstance(v, str) and v.strip():
                candidate_html = v
                break
        
        # nested data
        if not candidate_html and isinstance(result_obj.get('data'), dict):
            for k in priority_keys:
                v = result_obj['data'].get(k)
                if isinstance(v, str) and v.strip():
                    candidate_html = v
                    break
        
        # results.* uyumluluk
        if not candidate_html and isinstance(result_obj.get('results'), dict):
            for k in priority_keys:
                v = result_obj['results'].get(k)
                if isinstance(v, str) and v.strip():
                    candidate_html = v
                    break
    
    if not candidate_html:
        return ''

    # Try BeautifulSoup first
    try:
        if HAS_BS4 and BeautifulSoup is not None:
            soup = BeautifulSoup(candidate_html, 'html.parser')
            found = _find_target_with_bs(soup)
            if found:
                style_html, target_html = found if isinstance(found, tuple) else ('', found)
                combined = (style_html or '') + (target_html or '')
                return _sanitize_html(combined)
        
        # regex fallback
        extracted = _extract_by_regex(candidate_html)
        if extracted:
            return _sanitize_html(extracted)
        
        # fallback: calculation-results div'ini bulup çıkarmaya çalış, bulunamazsa tüm HTML'i temizle
        # Önce calculation-results içeriğini direkt bulmaya çalış
        calc_result_match = re.search(r'<div[^>]*class=["\'][^"\']*calculation-results[^"\']*["\'][^>]*>(.*?)</div>', candidate_html, flags=re.IGNORECASE | re.DOTALL)
        if calc_result_match:
            # calculation-results bulundu - sadece içini al ve wrap et
            inner_content = calc_result_match.group(1)
            cleaned = f'<div class="calculation-results">{inner_content}</div>'
            return _sanitize_html(cleaned)
        
        # calculation-results bulunamadı - modal wrapper'ları kaldırmaya çalış
        modal_patterns = [
            r'<div[^>]*class=["\'][^"\']*modal[^"\']*["\'][^>]*>\s*(.*?)\s*</div>',
            r'<div[^>]*class=["\'][^"\']*modal-dialog[^"\']*["\'][^>]*>\s*(.*?)\s*</div>',
            r'<div[^>]*class=["\'][^"\']*modal-content[^"\']*["\'][^>]*>\s*(.*?)\s*</div>',
            r'<div[^>]*class=["\'][^"\']*sc-[^"\']+[^"\']*["\'][^>]*>\s*(.*?)\s*</div>',
        ]
        
        cleaned = candidate_html
        for pattern in modal_patterns:
            # Nested replacement - içindeki content'i koruyarak wrapper'ı çıkar
            while True:
                old_cleaned = cleaned
                cleaned = re.sub(pattern, r'\1', cleaned, flags=re.IGNORECASE | re.DOTALL)
                if cleaned == old_cleaned:
                    break
        
        sanitized = _sanitize_html(cleaned)
        if len(sanitized.strip()) < 5:
            return _sanitize_html(candidate_html)
        
        return sanitized
    except Exception as e:
        logger.error(f"HTML extraction error: {e}")
        return _sanitize_html(candidate_html)
