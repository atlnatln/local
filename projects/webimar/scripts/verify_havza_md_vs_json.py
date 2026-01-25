#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""MD kaynağı ile public JSON çıktısının tutarlılığını doğrular.

Amaç:
- `webimar-nextjs/data/2026 havza ürün deseni.md` içindeki her (il/ilçe) satırı,
  `webimar-nextjs/public/havza_urun_desen.json` içinde bulunuyor mu?
- Ürün listeleri (parantez içleri atıldıktan sonra) birebir aynı mı?

Not: Üretim scriptindeki il/ilçe düzeltmelerini (fixes) burada da uygular.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

MD_PATH = Path("/home/akn/vps/projects/webimar/webimar-nextjs/data/2026 havza ürün deseni.md")
JSON_PATH = Path("/home/akn/vps/projects/webimar/webimar-nextjs/public/havza_urun_desen.json")

# Üretim scripti ile aynı düzeltmeler
TURKISH_FIXES = {
    "BALIKESIR": "BALIKESİR",
    "BILECIK": "BİLECİK",
    "BINGÖL": "BİNGÖL",
    "BITLIS": "BİTLİS",
    "DENIZLI": "DENİZLİ",
    "EDIRNE": "EDİRNE",
    "ERZINCAN": "ERZİNCAN",
    "ESKIŞEHIR": "ESKİŞEHİR",
    "GAZIANTEP": "GAZİANTEP",
    "GIRESUN": "GİRESUN",
    "GÜMÜŞHANE": "GÜMÜŞHANE",
    "KAYSERI": "KAYSERİ",
    "KILIS": "KİLİS",
    "KIRŞEHIR": "KIRŞEHİR",
    "MANISA": "MANİSA",
    "MERSIN": "MERSİN",
    "NIĞDE": "NİĞDE",
    "SIIRT": "SİİRT",
    "SINOP": "SİNOP",
    "SIVAS": "SİVAS",
    "TEKIRDAĞ": "TEKİRDAĞ",
    "TUNCELI": "TUNCELİ",
    "İZMIR": "İZMİR",
    "OSMANIYE": "OSMANIYE",
}

ILCE_FIXES = {
    "ALTEYÜL": "ALTIEYLÜL",
    "ALTEYUL": "ALTIEYLÜL",
    "BOZIYÜK": "BOZÜYÜK",
    "BOZIYUK": "BOZÜYÜK",
    "KARAMALI": "KARAMANLI",
    "TEFFENI": "TEFENNİ",
    "TEFFENİ": "TEFENNİ",
    "KOVANCLAR": "KOVANCILAR",
    "MIHALÇIÇIK": "MİHALIÇÇIK",
    "SEREFLIKOÇHISAR": "ŞEREFLİKOÇHİSAR",
    "DERBEN": "DERBENT",
}

TURKISH_FIXES_BY_NORM = {}
ILCE_FIXES_BY_NORM = {}

TR_UPPER = str.maketrans({"i": "İ", "ı": "I"})
TR_KEY = str.maketrans(
    {
        "İ": "I",
        "I": "I",
        "ı": "I",
        "i": "I",
        "Ö": "O",
        "ö": "O",
        "Ü": "U",
        "ü": "U",
        "Ç": "C",
        "ç": "C",
        "Ş": "S",
        "ş": "S",
        "Ğ": "G",
        "ğ": "G",
        "Â": "A",
        "â": "A",
        "Î": "I",
        "î": "I",
        "Û": "U",
        "û": "U",
    }
)


def to_tr_upper(s: str) -> str:
    return s.translate(TR_UPPER).upper()


def norm_key(s: str) -> str:
    s = to_tr_upper(s).strip()
    s = re.sub(r"\s+", "", s)
    s = s.translate(TR_KEY)
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def norm_product(s: str) -> str:
    s = s.strip()
    s = re.sub(r"\s*\([^)]*\)\s*", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().casefold()


def parse_md() -> dict[str, dict[str, list[str]]]:
    md_map: dict[str, dict[str, list[str]]] = defaultdict(dict)
    rows = 0

    text = MD_PATH.read_text(encoding="utf-8")
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        if "-----" in line or "HAVZA ADI" in line or "PLANLAMAYA" in line:
            continue

        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue

        havza_adi = parts[1].strip()
        urun_deseni = parts[2].strip()
        if not havza_adi or not urun_deseni or "/" not in havza_adi:
            continue

        sehir_raw, ilce_raw = [x.strip() for x in havza_adi.split("/", 1)]

        sehir = to_tr_upper(sehir_raw)
        ilce = to_tr_upper(ilce_raw)

        if ilce.endswith("*"):
            ilce = ilce[:-1].strip()

        # Düzeltmeleri normalize anahtar üzerinden uygula (İ/i ve benzeri varyantlara dayanıklı)
        sehir_fix = TURKISH_FIXES_BY_NORM.get(norm_key(sehir))
        if sehir_fix:
            sehir = sehir_fix

        ilce_fix = ILCE_FIXES_BY_NORM.get(norm_key(ilce))
        if ilce_fix:
            ilce = ilce_fix

        urunler_text = re.sub(r"\s*\([^)]+\)", "", urun_deseni)
        urunler = [u.strip() for u in urunler_text.split(",") if u.strip()]
        if not urunler:
            continue

        rows += 1
        md_map[norm_key(sehir)][norm_key(ilce)] = [norm_product(u) for u in urunler]

    print(f"MD satır sayısı: {rows}")
    return md_map


def parse_json() -> dict[str, dict[str, list[str]]]:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    json_map: dict[str, dict[str, list[str]]] = defaultdict(dict)

    for il, ilceler in data.items():
        for ilce, urunler in (ilceler or {}).items():
            json_map[norm_key(il)][norm_key(ilce)] = [norm_product(u) for u in urunler]

    print(f"JSON il sayısı (ham): {len(data)}")
    return json_map


def main() -> int:
    if not MD_PATH.exists():
        raise SystemExit(f"MD bulunamadı: {MD_PATH}")
    if not JSON_PATH.exists():
        raise SystemExit(f"JSON bulunamadı: {JSON_PATH}")

    # Fix map'lerini normalize anahtarlarla hazırla
    global TURKISH_FIXES_BY_NORM, ILCE_FIXES_BY_NORM
    TURKISH_FIXES_BY_NORM = {norm_key(k): v for k, v in TURKISH_FIXES.items()}
    ILCE_FIXES_BY_NORM = {norm_key(k): v for k, v in ILCE_FIXES.items()}

    md_map = parse_md()
    json_map = parse_json()

    missing: list[tuple[str, str]] = []
    prod_mismatch: list[tuple[str, str, int, int]] = []

    for il_k, ilceler in md_map.items():
        for ilce_k, md_urunler in ilceler.items():
            if il_k not in json_map or ilce_k not in json_map[il_k]:
                missing.append((il_k, ilce_k))
                continue
            j_urunler = json_map[il_k][ilce_k]
            md_set = set(md_urunler)
            j_set = set(j_urunler)
            if md_set - j_set or j_set - md_set:
                prod_mismatch.append((il_k, ilce_k, len(md_set - j_set), len(j_set - md_set)))

    print(f"MD il sayısı (normalize): {len(md_map)}")
    print(f"JSON il sayısı (normalize): {len(json_map)}")
    print(f"Eksik il/ilçe: {len(missing)}")
    print(f"Ürün farkı olan il/ilçe: {len(prod_mismatch)}")

    if missing:
        print("\nÖrnek eksikler (ilk 20):")
        for il_k, ilce_k in missing[:20]:
            print(f"- {il_k}/{ilce_k}")

    if prod_mismatch:
        print("\nÖrnek ürün farkları (ilk 20):")
        for il_k, ilce_k, a, b in prod_mismatch[:20]:
            print(f"- {il_k}/{ilce_k} (MD→JSON eksik: {a}, JSON→MD fazla: {b})")

    return 0 if (not missing and not prod_mismatch) else 2


if __name__ == "__main__":
    raise SystemExit(main())
