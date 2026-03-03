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

from apps.providers.domain_blacklist import (
    EXCLUDED_SCRAPE_DOMAINS,
    is_excluded_for_scrape,
    is_excluded_official_website_candidate,
)

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
    r"example\.com|example\.org|example\.net|"
    r"yoursite\.com|yourdomain\.com|youremail\.com|your-domain\.com|"
    r"sitename\.com|domain\.com|test\.com|sample\.com|"
    r"@sentry|sentry\.io|wixpress\.com|"
    r"placeholder|w3\.org|schema\.org|cloudflare\.com|"
    r"@webpack|@babel|@jest|\.png@|\.jpg@|\.gif@|\.svg@|"
    r"@[a-z0-9._%+\-]+\.(png|jpg|jpeg|gif|svg|webp|ico|css|js)$|"
    r"privacy@|abuse@|postmaster@|webmaster@)",
    re.IGNORECASE,
)

# Türkiye telefon regex: +90 / 0090 / 0 ile başlayan 10/11 haneli numaralar
_PHONE_RE = re.compile(
    r"""
    (?<![\d])          # rakamla başlamamalı
    (?:
        \+90           # uluslararası +90
        | 0090         # 0090 formatı
        | (?<!\+)\b0   # önünde + olmayan sıfır
    )
    [\s\-\.\u00a0(]*
    \d{3}              # alan/operatör kodu
    [\s\-\.\u00a0)]*
    \d{3}
    [\s\-\.\u00a0]*
    \d{2}
    [\s\-\.\u00a0]*
    \d{2}
    (?!\d)             # rakamla bitmemeli
    """,
    re.VERBOSE,
)

# Backward-compatible alias (merkezi listeyi kullan)
_EXCLUDED_SCRAPE_DOMAINS = EXCLUDED_SCRAPE_DOMAINS

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

_URL_RE = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)


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

        # last-call debug/telemetry (stage 4 sayaçları için)
        self.last_discovered_website: Optional[str] = None
        self.last_gemini_calls: int = 0
        # email kaynağı bilgisi (services.py tarafından BatchItem.data'ya yazılır)
        self.last_email_source_url: Optional[str] = None
        self.last_email_source_type: Optional[str] = None
        # telefon kaynağı bilgisi (web scraping ile bulunan)
        self.last_phone_source_url: Optional[str] = None
        self.last_phone_source_type: Optional[str] = None

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
        Geriye dönük uyumluluk için. Yalnızca email döner.
        Yeni kodda enrich_contacts() kullanın.
        """
        return self.enrich_contacts(firm_name, address, website_url).get("email")

    def enrich_contacts(
        self,
        firm_name: str,
        address: str = "",
        website_url: Optional[str] = None,
        existing_phone: Optional[str] = None,
    ) -> dict:
        """
        Email ve telefonu birlikte döndürür: {"email": str|None, "phone": str|None}

        Öncelik sırası (Gemini olmadan maksimum değer):
          S1 – website biliniyorsa doğrudan scrape (0 Gemini token)
          S2 – website yoksa Gemini ile resmi site bul → scrape (1 Gemini call)
          S3 – hâlâ email bulunamazsa Gemini grounding ile son çare arama
        """
        # reset metadata
        self.last_discovered_website = None
        self.last_gemini_calls = 0
        self.last_email_source_url = None
        self.last_email_source_type = None
        self.last_phone_source_url = None
        self.last_phone_source_type = None

        firm_name = (firm_name or "").strip()
        if not firm_name:
            return {"email": None, "phone": None}

        need_phone = not bool(existing_phone)
        result_email: Optional[str] = None
        result_phone: Optional[str] = None

        # S1: website biliniyorsa – 0 Gemini token
        if website_url:
            contacts = self._scrape_website_for_contacts(
                website_url, need_email=True, need_phone=need_phone
            )
            result_email = contacts["email"]
            result_phone = contacts["phone"]
            if result_email:
                self.last_email_source_url = website_url
                self.last_email_source_type = "scrape_website"
                logger.info("[EmailEnrich] S1-scrape  [%s] → email: %s", firm_name, result_email)
            if result_phone:
                self.last_phone_source_url = website_url
                self.last_phone_source_type = "scrape_website"
                logger.info("[EmailEnrich] S1-scrape  [%s] → phone: %s", firm_name, result_phone)
            if not result_email:
                logger.debug("[EmailEnrich] S1-scrape  [%s] → email not found, trying S2/S3", firm_name)

        # S2: website yoksa Gemini ile resmi site bul → scrape
        discovered_website: Optional[str] = None
        if not result_email and not website_url and self._api_key:
            discovered_website = self._gemini_find_official_website(firm_name, address)
            if discovered_website:
                self.last_discovered_website = discovered_website
                self.last_gemini_calls += 1
                contacts = self._scrape_website_for_contacts(
                    discovered_website, need_email=True, need_phone=need_phone
                )
                result_email = contacts["email"]
                if need_phone and not result_phone:
                    result_phone = contacts["phone"]
                if result_email:
                    self.last_email_source_url = discovered_website
                    self.last_email_source_type = "scrape_discovered"
                    logger.info(
                        "[EmailEnrich] S2-website→scrape [%s] → email: %s",
                        firm_name, result_email,
                    )
                if result_phone and not self.last_phone_source_url:
                    self.last_phone_source_url = discovered_website
                    self.last_phone_source_type = "scrape_discovered"
                    logger.info(
                        "[EmailEnrich] S2-website→scrape [%s] → phone: %s",
                        firm_name, result_phone,
                    )

        # S3: son çare — Gemini grounding ile email araması
        if not result_email:
            if not self._api_key:
                logger.warning("[EmailEnrich] GEMINI_API_KEY yok – S3 atlandı [%s]", firm_name)
            else:
                known_domain: Optional[str] = None
                domain_source_url = website_url or discovered_website
                if domain_source_url:
                    parsed = _base_url(domain_source_url)
                    if parsed:
                        from urllib.parse import urlparse as _up
                        known_domain = _up(parsed).netloc.lstrip("www.")

                result_email = self._gemini_search_email(firm_name, address, known_domain=known_domain)
                self.last_gemini_calls += 1
                if result_email:
                    self.last_email_source_url = getattr(self, "_last_s2_source_url", None) or "gemini-grounding"
                    self.last_email_source_type = getattr(self, "_last_s2_source_type", None) or "gemini_grounding"
                    logger.info("[EmailEnrich] S3-gemini  [%s] → email: %s", firm_name, result_email)
                else:
                    logger.debug("[EmailEnrich] S3-gemini  [%s] → not found", firm_name)

        return {"email": result_email, "phone": result_phone}

    def _gemini_find_official_website(self, firm_name: str, address: str) -> Optional[str]:
        """Gemini Search Grounding ile işletmenin resmi web sitesini bulur (URL veya None)."""
        try:
            from google import genai  # type: ignore
            from google.genai import types  # type: ignore
        except ImportError:
            logger.warning("[EmailEnrich] google-genai paketi kurulu değil – website araması atlandı")
            return None

        client = genai.Client(api_key=self._api_key)
        prompt = (
            "Aşağıdaki işletmenin resmi web sitesini Google Search ile bul. "
            "Sosyal medya, harita, dizin veya ilan sitelerini asla döndürme. "
            "Bulamazsan NONE döndür. Yalnızca tek satır döndür: URL veya NONE.\n\n"
            f"İşletme adı: {firm_name}\n"
            f"Adres: {address}\n"
        )

        try:
            response = client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=64,
                    tools=[{"google_search": {}}],
                ),
            )
        except Exception as exc:
            logger.warning("[EmailEnrich] Website grounding hatası [%s]: %s", firm_name, exc)
            self._log_token_event(
                firm_name=firm_name,
                address=address,
                known_domain=None,
                status="error",
                prompt_tokens=0,
                output_tokens=0,
                total_tokens=0,
                error=str(exc),
                extra={"event_type": "website_lookup"},
            )
            return None

        prompt_tokens, output_tokens, total_tokens = _extract_usage_tokens(response)
        self._log_token_event(
            firm_name=firm_name,
            address=address,
            known_domain=None,
            status="ok",
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            error="",
            extra={"event_type": "website_lookup"},
        )

        text = (getattr(response, "text", None) or "").strip()
        candidates: list[str] = []
        if text and text.upper() != "NONE":
            candidates.extend(_URL_RE.findall(text))
            if not candidates and "." in text and " " not in text:
                candidates.append(text)

        # grounding URL'lerini de aday olarak ekle
        candidates.extend(_get_grounding_urls(response))

        for raw in candidates:
            normalized = _normalize_public_url(raw)
            if normalized:
                return normalized

        return None

    # ------------------------------------------------------------------
    # Strategy 1 – web site scraping
    # ------------------------------------------------------------------

    def _scrape_website_for_contacts(
        self,
        website_url: str,
        need_email: bool = True,
        need_phone: bool = True,
    ) -> dict:
        """
        Web sitesini tarar; email ve/veya telefon arar.
        Sayfaları _CONTACT_PATHS sırasıyla dener.
        Email için: aynı domain'den veya açık info@ gibi adresler bulununca durur;
        gmail/hotmail adresi bulunsa bile daha iyi bir aday ararken devam eder.
        Returns: {"email": str|None, "phone": str|None}
        """
        base = _base_url(website_url)
        if not base:
            return {"email": None, "phone": None}

        try:
            from urllib.parse import urlparse as _up
            site_domain = _up(base).netloc.lstrip("www.")
        except Exception:
            site_domain = ""

        best_email: Optional[str] = None  # en iyi email adayı
        found_phone: Optional[str] = None

        for path in _CONTACT_PATHS:
            url = urljoin(base + "/", path.lstrip("/"))
            html = self._fetch_html(url)
            if not html:
                continue

            if need_email:
                candidate = _extract_best_email(html, source_url=url)
                if candidate:
                    cand_domain = candidate.split("@")[-1].lstrip("www.")
                    if best_email is None:
                        best_email = candidate  # ilk aday
                    # Daha iyi bir email bulunduysa güncelle:
                    # Kriter 1: Site domain'inden ise üstdür (kesin)
                    if cand_domain == site_domain:
                        best_email = candidate
                        if not need_phone or found_phone:
                            break  # en iyi email bulundu, telefon da bulunduysa dur
                    # Kriter 2: info/iletisim gibi prefix varsa gmail'den üstdür
                    info_prefixes = ("info", "iletisim", "iletişim", "contact", "mail", "bilgi")
                    if candidate.split("@")[0].lower().startswith(info_prefixes):
                        best_email = candidate

            if need_phone and not found_phone:
                found_phone = _extract_best_phone(html)

            # Kesin email (site domain'inden) ve telefon bulundu — dur
            if best_email and site_domain and best_email.split("@")[-1].lstrip("www.") == site_domain:
                if not need_phone or found_phone:
                    break

        return {"email": best_email, "phone": found_phone}

    def _scrape_website_for_email(self, website_url: str) -> Optional[str]:
        """Geriye dönük uyumluluk. Yalnızca email döner."""
        return self._scrape_website_for_contacts(
            website_url, need_email=True, need_phone=False
        )["email"]

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

        domain_hint = f" site:{known_domain}" if known_domain else ""
        prompt = (
            f'"{firm_name}" {address}{domain_hint} iletişim mail e-posta. '
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
                self._last_s2_source_url = "gemini-direct"
                self._last_s2_source_type = "gemini_direct"
                return email

        # Grounding chunk URL'lerini scrape et (max 3)
        chunk_urls = _get_grounding_urls(response)
        for url in chunk_urls[:3]:
            html = self._fetch_html(url)
            if not html:
                continue
            email = _extract_best_email(html, source_url=url)
            if email:
                self._last_s2_source_url = url
                self._last_s2_source_type = "gemini_grounding"
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
        extra: Optional[dict] = None,
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

        if extra and isinstance(extra, dict):
            for key, value in extra.items():
                if key not in event:
                    event[key] = value

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
        """
        URL'yi güvenli şekilde çeker.
        SSL sertifikası bozuk siteler için yeni bir session + verify=False ile fallback yapar.
        """
        if _is_excluded_domain(url):
            return None

        import random
        import time as _time_mod
        _time_mod.sleep(random.uniform(0.5, 1.5))  # Anti-Ban: Rastgele gecikme

        def _do_get(session: requests.Session, verify: bool) -> Optional[str]:
            try:
                resp = session.get(
                    url,
                    timeout=_SCRAPE_TIMEOUT,
                    stream=True,
                    allow_redirects=True,
                    verify=verify,
                )
                # Anti-Ban: Bot koruması varsa zorlama
                if resp.status_code in (403, 406, 429):
                    logger.debug("[EmailEnrich] Anti-bot [%s]: %s", resp.status_code, url)
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

            except requests.exceptions.SSLError:
                if verify:
                    # SSL sertifikası bozuk KOBİ siteleri için yeni session + verify=False
                    logger.warning(
                        "[EmailEnrich] SSL doğrulama hatası, verify=False ile yeniden deneniyor: %s", url
                    )
                    fallback_session = _build_session()
                    return _do_get(fallback_session, verify=False)
                logger.debug("[EmailEnrich] SSL fallback da başarısız: %s", url)
                return None
            except Exception as exc:
                logger.debug("[EmailEnrich] Fetch hatası [%s]: %s", url, exc)
                return None

        return _do_get(self._session, verify=True)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _build_session() -> requests.Session:
    session = requests.Session()
    # Anti-Ban: Gerçek bir Chrome tarayıcısı gibi davran
    # Not: "br" (Brotli) kaldırıldı — Python brotli paketi olmadan içeriği çözümleyemeyiz
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
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


def _normalize_public_url(raw_url: str) -> Optional[str]:
    """Gemini/grounding çıktısından gelen URL adayını normalize eder ve riskli domainleri eler."""
    raw_url = (raw_url or "").strip().strip(".,;)")
    if not raw_url:
        return None

    if not raw_url.startswith(("http://", "https://")):
        raw_url = f"https://{raw_url}"

    try:
        parsed = urlparse(raw_url)
    except Exception:
        return None

    if not parsed.netloc:
        return None

    if is_excluded_official_website_candidate(raw_url):
        return None

    # path varsa koru, query/fragment’i at (daha deterministik)
    path = parsed.path or ""
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def _is_excluded_domain(url: str) -> bool:
    return is_excluded_for_scrape(url)


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


def _normalize_phone(raw: str) -> Optional[str]:
    """
    Ham telefon metnini standart Türk formatına dönüştürür: 0XXX XXX XX XX
    Geçersiz uzunluktaki numaraları None döndürür.
    """
    digits = re.sub(r"\D", "", raw)
    # +905321234567 veya 00905321234567 → 05321234567
    if digits.startswith("90") and len(digits) == 12:
        digits = "0" + digits[2:]
    elif digits.startswith("0090") and len(digits) == 14:
        digits = "0" + digits[4:]
    # 5321234567 (10 hane, 0 yok) → 05321234567
    if len(digits) == 10 and digits[0] != "0":
        digits = "0" + digits
    if len(digits) != 11 or digits[0] != "0":
        return None
    return f"{digits[0:4]} {digits[4:7]} {digits[7:9]} {digits[9:11]}"


def _extract_best_phone(text: str) -> Optional[str]:
    """
    Metinden en iyi Türk telefon numarasını çıkarır.
    Öncelik: mobil hatlar (05xx) → diğer.
    """
    matches = _PHONE_RE.findall(text or "")
    phones: list[str] = []
    seen: set[str] = set()
    for raw in matches:
        normalized = _normalize_phone(raw.strip())
        if normalized and normalized not in seen:
            seen.add(normalized)
            phones.append(normalized)
    if not phones:
        return None
    # Mobil hatlara (05xx) öncelik ver
    mobile = [p for p in phones if p.startswith("05")]
    return (mobile or phones)[0]


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
