"""
Email Enrichment Provider
=========================

İki stratejili email bulma servisi:

Strateji 1 – Web sitesi zaten biliniyorsa (0 Gemini token):
  HTTP GET ile /iletisim, /contact, /about sayfalarını çek.
  Sayfadan regex ile email adresini çıkar.

Strateji 2 – Web sitesi bilinmiyorsa (1 Gemini çağrısı):
  Gemini Search Grounding ile '"{işletme adı}" email iletişim' araması yap.
  grounding_chunks içinden gelen ilk site URL'lerini HTTP ile çek.
  Sayfadan email çıkar.

Ayarlar (.env):
  GEMINI_API_KEY          – Gemini API anahtarı
  ANKA_EMAIL_MODEL        – Gemini model adı (varsayılan: gemini-2.5-flash)
  ANKA_EMAIL_ENRICHMENT_ENABLED   – True/False (varsayılan: True)
"""

import logging
import os
import re
import time
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex & Filtreler
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}",
    re.IGNORECASE,
)

# Bunlar gerçek işletme emaili sayılmaz
_JUNK_RE = re.compile(
    r"(noreply|no-reply|donotreply|do-not-reply|"
    r"example\.com|@sentry|sentry\.io|wixpress\.com|"
    r"placeholder|w3\.org|schema\.org|cloudflare\.com|"
    r"@webpack|@babel|@jest|\.png@|\.jpg@|\.gif@|\.svg@|"
    r"privacy@|abuse@|postmaster@|webmaster@)",
    re.IGNORECASE,
)

# Bu domainleri scrape etme
_EXCLUDED_SCRAPE_DOMAINS = frozenset(
    {
        "google.com",
        "google.com.tr",
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
        "linkedin.com",
        "youtube.com",
        "tiktok.com",
        "yandex.com",
        "bing.com",
        "wikipedia.org",
        "tripadvisor.com",
        "yelp.com",
        "foursquare.com",
        "maps.google.com",
        "goo.gl",
        "bit.ly",
        "t.co",
        "sahibinden.com",
        "hepsiburada.com",
        "n11.com",
        "gittigidiyor.com",
        "isbank.com.tr",
        "garanti.com.tr",
    }
)

# İletişim sayfaları – bu sırada denenir
_CONTACT_PATHS = [
    "/iletisim",
    "/iletişim",
    "/contact",
    "/contact-us",
    "/hakkimizda",
    "/hakkında",
    "/about",
    "/about-us",
    "/",
]

_SCRAPE_TIMEOUT = 6          # saniye
_MAX_SCRAPE_BYTES = 200_000  # 200 KB


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class EmailEnrichmentClient:
    """
    İşletme adına (ve varsa web sitesine) bakarak email adresi bulan servis.

    Kullanım örneği::

        client = EmailEnrichmentClient()
        email = client.enrich(
            firm_name="Planevi Şehircilik",
            address="Çankaya / Ankara",
            website_url=None,   # ya da "https://planevi.com.tr"
        )
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        requests_session: Optional[requests.Session] = None,
    ):
        self._api_key = (
            api_key
            or getattr(settings, "GEMINI_API_KEY", None)
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self._model = (
            model
            or os.environ.get("ANKA_EMAIL_MODEL")
            or getattr(settings, "ANKA_EMAIL_MODEL", "gemini-2.5-flash")
        )
        self._session = requests_session or _build_session()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enrich(
        self,
        firm_name: str,
        address: str = "",
        website_url: Optional[str] = None,
    ) -> Optional[str]:
        """
        En iyi email adresini döndürür, bulunamazsa None.

        Önce Strategy 1 (scrape), başarısızsa Strategy 2 (Gemini grounding)
        denenir.
        """
        firm_name = (firm_name or "").strip()
        if not firm_name:
            return None

        # Strategy 1: website biliniyorsa – 0 Gemini token
        if website_url:
            email = self._scrape_website_for_email(website_url)
            if email:
                logger.info("[EmailEnrich] S1-scrape  [%s] → %s", firm_name, email)
                return email
            logger.debug("[EmailEnrich] S1-scrape  [%s] → not found, trying S2", firm_name)

        # Strategy 2: Gemini grounding araması
        if not self._api_key:
            logger.warning(
                "[EmailEnrich] GEMINI_API_KEY yok – S2 atlandı [%s]", firm_name
            )
            return None

        email = self._gemini_search_email(firm_name, address)
        if email:
            logger.info("[EmailEnrich] S2-gemini  [%s] → %s", firm_name, email)
        else:
            logger.debug("[EmailEnrich] S2-gemini  [%s] → not found", firm_name)
        return email

    # ------------------------------------------------------------------
    # Strategy 1 – web site scraping
    # ------------------------------------------------------------------

    def _scrape_website_for_email(self, website_url: str) -> Optional[str]:
        base = _base_url(website_url)
        if not base:
            return None

        for path in _CONTACT_PATHS:
            url = urljoin(base + "/", path.lstrip("/"))
            html = self._fetch_html(url)
            if not html:
                continue
            email = _extract_best_email(html, source_url=url)
            if email:
                return email

        return None

    # ------------------------------------------------------------------
    # Strategy 2 – Gemini Search Grounding
    # ------------------------------------------------------------------

    def _gemini_search_email(self, firm_name: str, address: str) -> Optional[str]:
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except ImportError:
            logger.warning(
                "[EmailEnrich] google-genai paketi kurulu değil – S2 atlandı"
            )
            return None

        client = genai.Client(api_key=self._api_key)
        prompt = (
            f'"{firm_name}" adlı işletmenin resmi iletişim email adresini bul. '
            f"Adres: {address}. "
            "Kurumsal web sitesi tercih edilmeli. "
            "Sosyal medya ve genel rehber sitelerini döndürme. "
            "Sadece email adresini döndür, bulamazsan NONE yaz."
        )

        try:
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=64,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
        except Exception as exc:
            logger.warning(
                "[EmailEnrich] Gemini grounding hatası [%s]: %s", firm_name, exc
            )
            return None

        # Modelin doğrudan metin cevabında email var mı?
        text = (getattr(response, "text", None) or "").strip()
        if text.upper() != "NONE":
            email = _extract_best_email(text, source_url="gemini-response")
            if email:
                return email

        # Grounding chunk URL'lerini scrape et (max 3)
        chunk_urls = _get_grounding_urls(response)
        for url in chunk_urls[:3]:
            html = self._fetch_html(url)
            if not html:
                continue
            email = _extract_best_email(html, source_url=url)
            if email:
                return email

        return None

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> Optional[str]:
        """URL'yi güvenli şekilde çek. Hata durumunda None döner."""
        if _is_excluded_domain(url):
            return None
        try:
            resp = self._session.get(
                url,
                timeout=_SCRAPE_TIMEOUT,
                stream=True,
                allow_redirects=True,
            )
            resp.raise_for_status()

            chunks: list[bytes] = []
            total = 0
            for chunk in resp.iter_content(chunk_size=8192, decode_unicode=False):
                total += len(chunk)
                chunks.append(chunk)
                if total >= _MAX_SCRAPE_BYTES:
                    break

            raw = b"".join(chunks)
            encoding = resp.encoding or "utf-8"
            return raw.decode(encoding, errors="replace")

        except Exception as exc:
            logger.debug("[EmailEnrich] Fetch hatası [%s]: %s", url, exc)
            return None


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (compatible; AnkaBot/1.0; "
                "+https://ankadata.com.tr)"
            ),
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
    )
    return session


def _base_url(url: str) -> Optional[str]:
    """https://domain.com kısmını döndürür."""
    try:
        u = url if "://" in url else f"https://{url}"
        parsed = urlparse(u)
        if parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
    except Exception:
        pass
    return None


def _is_excluded_domain(url: str) -> bool:
    try:
        domain = urlparse(url).netloc.lower().lstrip("www.")
        return any(
            domain == ex or domain.endswith(f".{ex}")
            for ex in _EXCLUDED_SCRAPE_DOMAINS
        )
    except Exception:
        return False


def _extract_best_email(text: str, source_url: str = "") -> Optional[str]:
    """
    Metinden en iyi email adresini çıkarır.

    Öncelik: source_url ile aynı domain → info/iletisim ile başlayanlar → ilk temiz email.
    """
    matches = _EMAIL_RE.findall(text or "")
    if not matches:
        return None

    clean = [m for m in matches if not _JUNK_RE.search(m)]
    if not clean:
        return None

    # source ile aynı domaindekileri öne al
    source_domain = ""
    try:
        source_domain = urlparse(source_url).netloc.lower().lstrip("www.")
    except Exception:
        pass

    domain_local = [
        m
        for m in clean
        if source_domain and m.split("@")[-1].lower().lstrip("www.") == source_domain
    ]

    # info/iletisim/contact ön eki olanlara öncelik
    priority_prefixes = ("info", "iletisim", "iletişim", "contact", "mail", "bilgi")
    preferred = [
        m for m in (domain_local or clean) if m.split("@")[0].lower().startswith(priority_prefixes)
    ]

    result = (preferred or domain_local or clean)[0]
    return result.lower()


def _get_grounding_urls(response) -> list[str]:
    """Gemini response içindeki grounding chunk URL'lerini döndürür."""
    urls: list[str] = []
    try:
        response_candidates = getattr(response, "candidates", None) or []
        if not response_candidates:
            return urls
        metadata = getattr(response_candidates[0], "grounding_metadata", None)
        chunks = getattr(metadata, "grounding_chunks", None) or []
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            uri = getattr(web, "uri", None) if web else None
            if uri:
                urls.append(uri)
    except Exception:
        pass
    return urls
