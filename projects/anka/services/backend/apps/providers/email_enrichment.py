"""
Email Enrichment Provider
=========================

İki stratejili email bulma servisi:

Strateji 1 – Web sitesi zaten biliniyorsa (0 Gemini token):
  HTTP GET ile /iletisim, /contact, /about sayfalarını çek.
  Sayfadan regex ile email adresini çıkar.

Strateji 2 – Web sitesi bilinmiyorsa (1 Gemini çağrısı):
    Gemini Search Grounding ile '"{işletme adı}" {adres} iletişim mail e-posta' araması yap.
  grounding_chunks içinden gelen ilk site URL'lerini HTTP ile çek.
  Sayfadan email çıkar.

Ayarlar (.env):
  GEMINI_API_KEY          – Gemini API anahtarı
  ANKA_EMAIL_MODEL        – Gemini model adı (varsayılan: gemini-2.5-flash)
  ANKA_EMAIL_ENRICHMENT_ENABLED   – True/False (varsayılan: True)
    ANKA_EMAIL_TOKEN_LOG_ENABLED    – Token JSONL log açık/kapalı
    ANKA_EMAIL_TOKEN_LOG_PATH       – Token JSONL dosya yolu
    ANKA_EMAIL_DAILY_TOKEN_LIMIT    – Günlük toplam token limiti (0=sınırsız)
    ANKA_EMAIL_TOKEN_WARN_THRESHOLD – Limit uyarı eşiği (0..1)
"""

import logging
import os
import re
import json
from datetime import datetime
from pathlib import Path
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
    r"@[a-z0-9._%+\-]+\.(png|jpg|jpeg|gif|svg|webp|ico|css|js)$|"
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
    "/iletisim.php",
    "/iletisim.html",
    "/iletişim",
    "/bize-ulasin",
    "/bize_ulasin",
    "/contact",
    "/contact-us",
    "/contact.html",
    "/contact.php",
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
        self._token_log_enabled = _env_bool(
            "ANKA_EMAIL_TOKEN_LOG_ENABLED",
            getattr(settings, "ANKA_EMAIL_TOKEN_LOG_ENABLED", True),
        )
        self._daily_token_limit = _env_int(
            "ANKA_EMAIL_DAILY_TOKEN_LIMIT",
            getattr(settings, "ANKA_EMAIL_DAILY_TOKEN_LIMIT", 0),
        )
        self._token_warn_threshold = _env_float(
            "ANKA_EMAIL_TOKEN_WARN_THRESHOLD",
            getattr(settings, "ANKA_EMAIL_TOKEN_WARN_THRESHOLD", 0.8),
        )
        self._token_log_path = _resolve_token_log_path(
            os.environ.get("ANKA_EMAIL_TOKEN_LOG_PATH")
            or getattr(settings, "ANKA_EMAIL_TOKEN_LOG_PATH", "")
        )

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

        # website biliniyorsa domain bilgisini Gemini'ye ilet (site: hedefli arama)
        known_domain: Optional[str] = None
        if website_url:
            parsed_domain = _base_url(website_url)
            if parsed_domain:
                from urllib.parse import urlparse as _up
                known_domain = _up(parsed_domain).netloc.lstrip("www.")

        email = self._gemini_search_email(firm_name, address, known_domain=known_domain)
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

    def _gemini_search_email(
        self,
        firm_name: str,
        address: str,
        known_domain: Optional[str] = None,
    ) -> Optional[str]:
        today_used_tokens = self._get_today_token_usage()
        if self._daily_token_limit > 0 and today_used_tokens >= self._daily_token_limit:
            logger.warning(
                "[EmailEnrich] Token limiti aşıldı (%s/%s) – S2 atlandı [%s]",
                today_used_tokens,
                self._daily_token_limit,
                firm_name,
            )
            return None

        if self._daily_token_limit > 0 and today_used_tokens >= int(self._daily_token_limit * self._token_warn_threshold):
            logger.warning(
                "[EmailEnrich] Token kullanımı uyarı eşiğinde (%s/%s, %.0f%%)",
                today_used_tokens,
                self._daily_token_limit,
                self._token_warn_threshold * 100,
            )

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
            f'"{firm_name}" {address} iletişim mail e-posta. '
            "Arama sonuçlarındaki en alakalı resmi iletişim sayfasının linkini ve email adresini bul. "
            "Sosyal medya (facebook, instagram vb.) ve rehber sitelerini (bulurum.com vb.) yoksay. "
            "Sadece email adresini döndür, bulamazsan NONE yaz."
        )

        try:
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    tools=[{"google_search": {}}],
                ),
            )
        except Exception as exc:
            logger.warning(
                "[EmailEnrich] Gemini grounding hatası [%s]: %s", firm_name, exc
            )
            self._log_token_event(
                firm_name=firm_name,
                address=address,
                known_domain=known_domain,
                status="error",
                prompt_tokens=0,
                output_tokens=0,
                total_tokens=0,
                error=str(exc),
            )
            return None

        prompt_tokens, output_tokens, total_tokens = _extract_usage_tokens(response)
        self._log_token_event(
            firm_name=firm_name,
            address=address,
            known_domain=known_domain,
            status="ok",
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            error="",
        )

        if total_tokens > 0:
            logger.info(
                "[EmailEnrich] Token usage [%s]: prompt=%s output=%s total=%s",
                firm_name,
                prompt_tokens,
                output_tokens,
                total_tokens,
            )

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

    def _get_today_token_usage(self) -> int:
        if not self._token_log_enabled:
            return 0
        if not self._token_log_path.exists():
            return 0

        today = datetime.now().strftime("%Y-%m-%d")
        total = 0
        try:
            with self._token_log_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        row = json.loads(line)
                    except Exception:
                        continue
                    if not str(row.get("timestamp", "")).startswith(today):
                        continue
                    total += int(row.get("total_tokens", 0) or 0)
        except Exception as exc:
            logger.debug("[EmailEnrich] Token log okunamadı: %s", exc)
            return 0

        return total

    def _log_token_event(
        self,
        firm_name: str,
        address: str,
        known_domain: Optional[str],
        status: str,
        prompt_tokens: int,
        output_tokens: int,
        total_tokens: int,
        error: str,
    ) -> None:
        if not self._token_log_enabled:
            return

        event = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "model": self._model,
            "status": status,
            "firm_name": firm_name,
            "address": address,
            "known_domain": known_domain or "",
            "prompt_tokens": int(prompt_tokens),
            "output_tokens": int(output_tokens),
            "total_tokens": int(total_tokens),
            "error": error,
        }

        try:
            self._token_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self._token_log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.debug("[EmailEnrich] Token log yazılamadı: %s", exc)

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _fetch_html(self, url: str) -> Optional[str]:
        """URL'yi güvenli şekilde çek. Hata durumunda None döner."""
        if _is_excluded_domain(url):
            return None
        try:
            import random
            import time
            time.sleep(random.uniform(0.5, 1.5))  # Anti-Ban: Rastgele gecikme
            
            resp = self._session.get(
                url,
                timeout=_SCRAPE_TIMEOUT,
                stream=True,
                allow_redirects=True,
            )
            # Anti-Ban: Bot koruması varsa zorlama
            if resp.status_code in (403, 406, 429):
                logger.debug("[EmailEnrich] Anti-bot detected [%s]: %s", resp.status_code, url)
                return None
                
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
    # Anti-Ban: Gerçek bir Chrome tarayıcısı gibi davran
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
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


def _extract_usage_tokens(response) -> tuple[int, int, int]:
    usage = getattr(response, "usage_metadata", None)
    if not usage:
        return 0, 0, 0

    prompt_tokens = (
        getattr(usage, "prompt_token_count", None)
        or getattr(usage, "input_tokens", None)
        or 0
    )
    output_tokens = (
        getattr(usage, "candidates_token_count", None)
        or getattr(usage, "output_tokens", None)
        or 0
    )
    total_tokens = (
        getattr(usage, "total_token_count", None)
        or (int(prompt_tokens) + int(output_tokens))
    )
    return int(prompt_tokens), int(output_tokens), int(total_tokens)


def _env_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key)
    if raw is None:
        return bool(default)
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.environ.get(key)
    if raw is None or raw == "":
        return int(default)
    try:
        return int(raw)
    except ValueError:
        return int(default)


def _env_float(key: str, default: float) -> float:
    raw = os.environ.get(key)
    if raw is None or raw == "":
        return float(default)
    try:
        value = float(raw)
    except ValueError:
        return float(default)
    if value < 0:
        return 0.0
    if value > 1:
        return 1.0
    return value


def _resolve_token_log_path(configured_path: str) -> Path:
    if configured_path:
        return Path(configured_path)

    base_dir = Path(getattr(settings, "BASE_DIR", "."))
    return base_dir / "artifacts" / "usage" / "email_enrichment_tokens.jsonl"
