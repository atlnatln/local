#!/usr/bin/env python3
"""Check sitemap URLs against a local base URL.

Usage:
  python3 scripts/check_sitemap_local.py \
    --sitemap webimar-nextjs/public/sitemap.xml \
    --base http://localhost:3000 \
    --timeout 10 \
    --concurrency 16

Defaults are set for the Webimar local dev stack.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sitemap",
        default="webimar-nextjs/public/sitemap.xml",
        help="Path to sitemap.xml (default: webimar-nextjs/public/sitemap.xml)",
    )
    parser.add_argument(
        "--base",
        default="http://localhost:3000",
        help="Base URL to test against (default: http://localhost:3000)",
    )
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--concurrency", type=int, default=16)
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Retry count for transient failures (default: 2)",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=0.4,
        help="Seconds to wait between retries (default: 0.4)",
    )
    return parser.parse_args()


def extract_locs(sitemap_path: str) -> list[str]:
    tree = ET.parse(sitemap_path)
    root = tree.getroot()

    # Namespace-agnostic: locate all <loc> elements.
    locs: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            locs.append(element.text.strip())
    return locs


def to_local_url(loc: str, base: str) -> str:
    parsed = urllib.parse.urlparse(loc)
    if not parsed.scheme or not parsed.netloc:
        # Already relative or malformed; just join.
        return urllib.parse.urljoin(base.rstrip("/") + "/", loc.lstrip("/"))

    base_parsed = urllib.parse.urlparse(base)
    local = parsed._replace(scheme=base_parsed.scheme, netloc=base_parsed.netloc)
    return urllib.parse.urlunparse(local)


def fetch(url: str, timeout: float) -> tuple[int, str]:
    # Try HEAD first; fallback to GET if unsupported.
    headers = {
        "User-Agent": "webimar-sitemap-check/1.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def do_request(method: str) -> tuple[int, str]:
        req = urllib.request.Request(url, method=method, headers=headers)
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, resp.geturl()

    try:
        return do_request("HEAD")
    except urllib.error.HTTPError as e:
        if e.code in (405, 501):
            try:
                return do_request("GET")
            except urllib.error.HTTPError as e2:
                return e2.code, getattr(e2, "url", url)
        return e.code, getattr(e, "url", url)
    except Exception:
        return 0, url


def fetch_with_retries(url: str, timeout: float, retries: int, retry_delay: float) -> tuple[int, str]:
    transient_codes = {0, 429, 500, 502, 503, 504}
    last_status = 0
    last_final = url
    for attempt in range(max(0, retries) + 1):
        status, final_url = fetch(url, timeout)
        last_status, last_final = status, final_url
        if status not in transient_codes:
            return status, final_url
        if attempt < retries:
            time.sleep(max(0.0, retry_delay))
    return last_status, last_final


def main() -> int:
    args = parse_args()

    locs = extract_locs(args.sitemap)
    if not locs:
        print("No <loc> entries found.", file=sys.stderr)
        return 2

    base = args.base.rstrip("/")
    start = time.time()

    rows: list[tuple[str, str, int, str]] = []

    def work(loc: str) -> tuple[str, str, int, str]:
        local_url = to_local_url(loc, base)
        status, final_url = fetch_with_retries(
            local_url,
            args.timeout,
            retries=args.retries,
            retry_delay=args.retry_delay,
        )
        return loc, local_url, status, final_url

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        futures = [ex.submit(work, loc) for loc in locs]
        for fut in concurrent.futures.as_completed(futures):
            rows.append(fut.result())

    rows.sort(key=lambda r: r[1])

    ok = []
    bad = []
    for loc, local_url, status, final_url in rows:
        if status in (200, 204, 301, 302, 307, 308):
            ok.append((loc, local_url, status, final_url))
        else:
            bad.append((loc, local_url, status, final_url))

    duration = time.time() - start
    print(f"Checked {len(rows)} URLs in {duration:.1f}s")
    print(f"OK: {len(ok)}")
    print(f"BAD: {len(bad)}")

    if bad:
        print("\n--- BAD URLS ---")
        for loc, local_url, status, final_url in bad:
            status_txt = str(status) if status else "ERR"
            print(f"{status_txt}\t{local_url}\t(from {loc})\t(final {final_url})")

    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
