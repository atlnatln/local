# HTML Sanitization utility
import html
import re
from typing import Dict, Any

def sanitize_html_content(content: str) -> str:
    """
    HTML içeriğini güvenli hale getirir
    XSS saldırılarına karşı koruma sağlar
    """
    if not content or not isinstance(content, str):
        return content
    
    # Potansiyel tehlikeli script taglarını ve javascript'i tamamen kaldır
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
    content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)  # onclick, onload vs.
    
    # HTML escape uygula
    sanitized = html.escape(content)
    
    # Sadece güvenli HTML taglerini geri getir
    allowed_tags = ['b', 'i', 'u', 'br', 'p', 'strong', 'em', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li']
    
    for tag in allowed_tags:
        # Açılış tagları
        sanitized = sanitized.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        sanitized = sanitized.replace(f'&lt;{tag.upper()}&gt;', f'<{tag}>')
        # Kapanış tagları
        sanitized = sanitized.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
        sanitized = sanitized.replace(f'&lt;/{tag.upper()}&gt;', f'</{tag}>')
    
    # CSS class attribute'larını güvenli şekilde geri getir (sadece alfa-numerik ve - _ karakterleri)
    sanitized = re.sub(r'&lt;(\w+)\s+class=&quot;([a-zA-Z0-9\-_\s]+)&quot;&gt;', r'<\1 class="\2">', sanitized)
    
    return sanitized

def sanitize_calculation_result(result_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Hesaplama sonucunda HTML mesajları güvenli hale getirir
    """
    if not isinstance(result_data, dict):
        return result_data
    
    sanitized_result = result_data.copy()
    
    # HTML mesajlarını sanitize et
    if 'html_mesaj' in sanitized_result and isinstance(sanitized_result['html_mesaj'], str):
        sanitized_result['html_mesaj'] = sanitize_html_content(sanitized_result['html_mesaj'])
    
    # Ana mesaj alanını da kontrol et
    if 'ana_mesaj' in sanitized_result and isinstance(sanitized_result['ana_mesaj'], str):
        sanitized_result['ana_mesaj'] = sanitize_html_content(sanitized_result['ana_mesaj'])
    
    return sanitized_result
