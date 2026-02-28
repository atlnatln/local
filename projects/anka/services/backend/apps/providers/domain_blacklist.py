"""Domain blacklist helpers.

Amaç:
- "Resmi website" ararken sosyal medya / dizin / ilan / harita / kısa-link gibi
  kaynakları dışlamak.
- Scraping aşamasında da aynı riskli domainleri atlamak.

Not: Bu dosya Django importlarına bağlı değildir (script'ler de kullanabilir).
"""

from __future__ import annotations

from urllib.parse import urlparse


EXCLUDED_SCRAPE_DOMAINS: frozenset[str] = frozenset(
    {
        # Search engines / maps / redirects
        "google.com",
        "google.com.tr",
        "maps.google.com",
        "goo.gl",
        "t.co",
        "bit.ly",
        "tinyurl.com",
        "lnkd.in",
        "l.facebook.com",
        "yandex.com",
        "bing.com",

        # Social
        "facebook.com",
        "instagram.com",
        "twitter.com",
        "x.com",
        "linkedin.com",
        "youtube.com",
        "tiktok.com",

        # Reviews / check-ins / directories
        "foursquare.com",
        "tripadvisor.com",
        "yelp.com",
        "wikipedia.org",
        "yellowpages.com",
        "infobel.com",
        "tuugo.com",

        # TR directories / aggregators (gözlenen + yaygın)
        "bulurum.com",
        "firmasec.com",
        "firmasec.com.tr",
        "firmarehberi.com",
        "firmarehberi.com.tr",
        "rehber.com",
        "rehber.com.tr",
        "ticaretrehberi.com",
        "ticaretrehberi.com.tr",
        "esnafrehberi.com",
        "esnafrehberi.com.tr",

        # Marketplaces (genelde resmi website değil)
        "sahibinden.com",
        "hepsiburada.com",
        "n11.com",

        # Banking / payments (yanlış pozitif risk)
        "isbank.com.tr",
        "garanti.com.tr",

        # Common false positives
        "schema.org",
        "w3.org",
        "cloudflare.com",
        "sentry.io",
        "wixpress.com",
    }
)


# Resmi website adayı olarak da asla kabul etmeyeceklerimiz.
# Scrape blacklist'i + daha agresif dizin/ilan/mapping kaynakları.
EXCLUDED_OFFICIAL_WEBSITE_DOMAINS: frozenset[str] = EXCLUDED_SCRAPE_DOMAINS


def _normalize_host(host: str) -> str:
    host = (host or "").strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def host_in_blacklist(host: str, blacklist: frozenset[str]) -> bool:
    host = _normalize_host(host)
    if not host:
        return True
    return any(host == blocked or host.endswith(f".{blocked}") for blocked in blacklist)


def url_host(url: str) -> str:
    try:
        parsed = urlparse(url)
    except Exception:
        return ""
    return _normalize_host(parsed.netloc)


def is_excluded_for_scrape(url_or_host: str) -> bool:
    host = url_or_host
    if "://" in url_or_host:
        host = url_host(url_or_host)
    return host_in_blacklist(host, EXCLUDED_SCRAPE_DOMAINS)


def is_excluded_official_website_candidate(url_or_host: str) -> bool:
    host = url_or_host
    if "://" in url_or_host:
        host = url_host(url_or_host)
    return host_in_blacklist(host, EXCLUDED_OFFICIAL_WEBSITE_DOMAINS)
