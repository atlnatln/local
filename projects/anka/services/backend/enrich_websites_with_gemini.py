#!/usr/bin/env python3
"""
Google Maps'ten çekilen CSV verilerinde website alanı boş olan işletmeler için
Gemini 2.0 Flash + Google Search Grounding kullanarak resmi web sitesi bulur.

Amaç: Sadece web sitesi URL'sini doldurmak (site içi scraping yok).
"""

import argparse
import csv
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlparse

from google import genai
from google.genai import types

URL_PATTERN = re.compile(r"https?://[^\s\]\)\"'<>]+", re.IGNORECASE)

EXCLUDED_DOMAINS = {
    "instagram.com",
    "facebook.com",
    "linkedin.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "tiktok.com",
    "maps.google.com",
    "google.com",
    "yelp.com",
    "foursquare.com",
    "tripadvisor.com",
    "wikipedia.org",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CSV içindeki boş website alanlarını Gemini Search Grounding ile doldurur."
    )
    parser.add_argument(
        "--input",
        default="data/google_maps_searches/query_3_20260201_165628/results.csv",
        help="Girdi CSV yolu (services/backend'e göre relatif veya mutlak).",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash",
        help="Kullanılacak model adı.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="İşlenecek maksimum boş website satırı (0 = sınırsız).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.25,
        help="İstekler arası bekleme (saniye).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="CSV'ye yazmadan sadece sonucu gösterir.",
    )
    parser.add_argument(
        "--api-key-env",
        default="GEMINI_API_KEY",
        help="Gemini API key için environment variable adı.",
    )
    parser.add_argument(
        "--usage-log",
        default="artifacts/usage/gemini_grounding_usage.jsonl",
        help="İstek/token kullanım log dosyası (JSONL).",
    )
    parser.add_argument(
        "--daily-request-limit",
        type=int,
        default=1500,
        help="Günlük request limiti. Bu sayıya ulaşınca işlem durur.",
    )
    parser.add_argument(
        "--daily-token-limit",
        type=int,
        default=0,
        help="Günlük token limiti (0 = kapalı).",
    )
    parser.add_argument(
        "--warn-threshold",
        type=float,
        default=0.8,
        help="Limit yüzdesi (0-1). Aşılırsa uyarı basılır (örn 0.8 = %%80).",
    )
    return parser.parse_args()


def resolve_csv_path(csv_path: str) -> Path:
    path = Path(csv_path)
    if path.is_absolute():
        return path
    return (Path(__file__).parent / path).resolve()


def resolve_output_path(file_path: str) -> Path:
    path = Path(file_path)
    if path.is_absolute():
        return path
    return (Path(__file__).parent / path).resolve()


def normalize_url(raw_url: str) -> Optional[str]:
    raw_url = raw_url.strip().strip(".,;)")
    if not raw_url:
        return None

    if not raw_url.startswith(("http://", "https://")):
        raw_url = f"https://{raw_url}"

    parsed = urlparse(raw_url)
    if not parsed.netloc:
        return None

    hostname = parsed.netloc.lower()
    if hostname.startswith("www."):
        hostname = hostname[4:]

    for blocked in EXCLUDED_DOMAINS:
        if hostname == blocked or hostname.endswith(f".{blocked}"):
            return None

    return f"{parsed.scheme}://{parsed.netloc}{parsed.path or ''}"


def extract_urls_from_text(text: str) -> Iterable[str]:
    for match in URL_PATTERN.findall(text or ""):
        yield match


def build_prompt(name: str, address: str) -> str:
    return (
        "Aşağıdaki işletmenin resmi web sitesini Google Search ile bul. "
        "Sosyal medya, harita, dizin veya ilan sitelerini asla döndürme. "
        "Eğer resmi bir web sitesi bulamazsan NONE döndür. "
        "Yalnızca tek satır döndür: URL veya NONE.\n\n"
        f"İşletme adı: {name}\n"
        f"Adres: {address}\n"
    )


def find_website(
    client: genai.Client,
    model: str,
    business_name: str,
    business_address: str,
) -> Optional[str]:
    response = client.models.generate_content(
        model=model,
        contents=build_prompt(business_name, business_address),
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=64,
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )

    candidates: list[str] = []

    text = (response.text or "").strip()
    if text.upper() != "NONE":
        candidates.extend(extract_urls_from_text(text))
        if text and not candidates and "." in text and " " not in text:
            candidates.append(text)

    first_candidate = None
    response_candidates = getattr(response, "candidates", None) or []
    if response_candidates:
        first_candidate = response_candidates[0]

    metadata = getattr(first_candidate, "grounding_metadata", None) if first_candidate else None
    chunks = getattr(metadata, "grounding_chunks", None) or []

    for chunk in chunks:
        web = getattr(chunk, "web", None)
        uri = getattr(web, "uri", None) if web else None
        if uri:
            candidates.append(uri)

    for raw in candidates:
        normalized = normalize_url(raw)
        if normalized:
            return normalized

    return None


def extract_usage_counts(response) -> tuple[int, int, int]:
    usage = getattr(response, "usage_metadata", None)
    if not usage:
        return 0, 0, 0

    prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
    total_tokens = int(getattr(usage, "total_token_count", prompt_tokens + output_tokens) or 0)
    return prompt_tokens, output_tokens, total_tokens


def append_usage_log(log_path: Path, payload: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(payload, ensure_ascii=False) + "\n")


def warn_if_threshold_exceeded(
    label: str,
    used: int,
    limit: int,
    warn_threshold: float,
) -> None:
    if limit <= 0:
        return

    ratio = used / limit
    if ratio >= warn_threshold:
        print(
            f"⚠️ UYARI: {label} kullanımı {used}/{limit} (%{ratio * 100:.1f}) seviyesine ulaştı."
        )


def main() -> int:
    args = parse_args()

    api_key = os.getenv(args.api_key_env) or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print(
            f"HATA: API key bulunamadı. '{args.api_key_env}' veya 'GOOGLE_API_KEY' tanımlayın."
        )
        return 1

    csv_path = resolve_csv_path(args.input)
    usage_log_path = resolve_output_path(args.usage_log)
    if not csv_path.exists():
        print(f"HATA: CSV bulunamadı: {csv_path}")
        return 1

    client = genai.Client(api_key=api_key)

    with csv_path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if not fieldnames:
        print("HATA: CSV başlıkları okunamadı.")
        return 1

    to_process = [row for row in rows if not (row.get("website") or "").strip()]
    if args.limit > 0:
        to_process = to_process[: args.limit]

    print(f"Toplam satır: {len(rows)}")
    print(f"Website boş satır: {sum(1 for row in rows if not (row.get('website') or '').strip())}")
    print(f"İşlenecek satır: {len(to_process)}")
    print(f"Kullanım logu: {usage_log_path}")

    filled_count = 0
    request_count = 0
    prompt_tokens_total = 0
    output_tokens_total = 0
    total_tokens_total = 0

    for index, row in enumerate(to_process, start=1):
        if args.daily_request_limit > 0 and request_count >= args.daily_request_limit:
            print("⛔ Request limiti aşıldı, işlem güvenli şekilde durduruldu.")
            break
        if args.daily_token_limit > 0 and total_tokens_total >= args.daily_token_limit:
            print("⛔ Token limiti aşıldı, işlem güvenli şekilde durduruldu.")
            break

        name = (row.get("name") or "").strip()
        address = (row.get("formatted_address") or "").strip()

        if not name:
            continue

        request_count += 1

        try:
            response = client.models.generate_content(
                model=args.model,
                contents=build_prompt(name, address),
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=64,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )

            prompt_tokens, output_tokens, total_tokens = extract_usage_counts(response)
            prompt_tokens_total += prompt_tokens
            output_tokens_total += output_tokens
            total_tokens_total += total_tokens

            found_website = None
            candidates: list[str] = []

            text = (response.text or "").strip()
            if text.upper() != "NONE":
                candidates.extend(extract_urls_from_text(text))
                if text and not candidates and "." in text and " " not in text:
                    candidates.append(text)

            response_candidates = getattr(response, "candidates", None) or []
            if response_candidates:
                metadata = getattr(response_candidates[0], "grounding_metadata", None)
                chunks = getattr(metadata, "grounding_chunks", None) or []
                for chunk in chunks:
                    web = getattr(chunk, "web", None)
                    uri = getattr(web, "uri", None) if web else None
                    if uri:
                        candidates.append(uri)

            for raw in candidates:
                normalized = normalize_url(raw)
                if normalized:
                    found_website = normalized
                    break

            append_usage_log(
                usage_log_path,
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": args.model,
                    "business_name": name,
                    "formatted_address": address,
                    "status": "success",
                    "website": found_website,
                    "request_index": request_count,
                    "prompt_tokens": prompt_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                },
            )

        except Exception as exc:
            print(f"[{index}/{len(to_process)}] HATA - {name}: {exc}")
            append_usage_log(
                usage_log_path,
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": args.model,
                    "business_name": name,
                    "formatted_address": address,
                    "status": "error",
                    "website": None,
                    "request_index": request_count,
                    "prompt_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "error": str(exc),
                },
            )
            if args.sleep > 0:
                time.sleep(args.sleep)
            continue

        if found_website:
            print(f"[{index}/{len(to_process)}] ✅ {name} -> {found_website}")
            row["website"] = found_website
            filled_count += 1
        else:
            print(f"[{index}/{len(to_process)}] ❌ {name} -> bulunamadı")

        if args.sleep > 0:
            time.sleep(args.sleep)

        warn_if_threshold_exceeded(
            "Request",
            request_count,
            args.daily_request_limit,
            args.warn_threshold,
        )
        warn_if_threshold_exceeded(
            "Token",
            total_tokens_total,
            args.daily_token_limit,
            args.warn_threshold,
        )

    if args.dry_run:
        print(f"\nDry-run tamamlandı. Bulunan website sayısı: {filled_count}")
        print(
            f"Kullanım özeti -> request: {request_count}, prompt_tokens: {prompt_tokens_total}, "
            f"output_tokens: {output_tokens_total}, total_tokens: {total_tokens_total}"
        )
        return 0

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nTamamlandı. Güncellenen website sayısı: {filled_count}")
    print(f"CSV güncellendi: {csv_path}")
    print(
        f"Kullanım özeti -> request: {request_count}, prompt_tokens: {prompt_tokens_total}, "
        f"output_tokens: {output_tokens_total}, total_tokens: {total_tokens_total}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
