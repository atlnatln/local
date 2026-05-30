#!/usr/bin/env python3
"""
Play Store API CLI

Komutlar:
    sync-listing  --app <app-id>   Store listing, details ve images'i API ile senkronize et
    release       --app <app-id> --aab <path>   AAB upload + track assignment
    scaffold      --app <app-id> --package <pkg> [--title <t>] [--lang <l>]
                  Yeni app için template klasörü oluştur
    validate      --app <app-id>   Metin uzunlukları ve görsel boyutlarını kontrol et

Örnek:
    python scripts/play-cli.py sync-listing --app mathlock-play
    python scripts/play-cli.py release --app mathlock-play --aab ../mathlock-play/app/build/outputs/bundle/release/app-release.aab
    python scripts/play-cli.py scaffold --app super-oyun --package com.akn.superoyun --title "Süper Oyun" --lang tr-TR
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ── Google API kütüphaneleri ──
try:
    import httplib2
    from google.oauth2 import service_account
    from google_auth_httplib2 import AuthorizedHttp
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
except ImportError as e:
    print(f"[HATA] Gerekli kütüphaneler eksik: {e}")
    print("Kurulum: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    sys.exit(1)

# ── Sabitler ──
BASE_DIR = Path(__file__).parent.parent.resolve()
APPS_DIR = BASE_DIR / "apps"

IMAGE_TYPES = {
    "icon": "icon",
    "featureGraphic": "featureGraphic",
    "phoneScreenshots": "phoneScreenshots",
    "sevenInchScreenshots": "sevenInchScreenshots",
    "tenInchScreenshots": "tenInchScreenshots",
}

MAX_LENGTHS = {
    "title": 30,
    "short_description": 80,
    "full_description": 4000,
}

# ═════════════════════════════════════════════════════════════════
#  YARDIMCI FONKSİYONLAR
# ═════════════════════════════════════════════════════════════════

def load_config(app_id: str) -> dict:
    config_path = APPS_DIR / app_id / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config bulunamadı: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["id"] = app_id
    return cfg


def resolve_service_account_path(config: dict) -> Path:
    sa = config.get("serviceAccount", "")
    if not sa:
        raise ValueError("'serviceAccount' config.json'de tanımlı değil.")
    p = Path(sa)
    if not p.is_absolute():
        p = (APPS_DIR / config["id"] / p).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Service account JSON bulunamadı: {p}")
    return p


def get_service(config: dict):
    sa_path = resolve_service_account_path(config)
    creds = service_account.Credentials.from_service_account_file(
        str(sa_path),
        scopes=["https://www.googleapis.com/auth/androidpublisher"],
    )
    http = httplib2.Http(timeout=120)
    auth_http = AuthorizedHttp(creds, http=http)
    return build("androidpublisher", "v3", http=auth_http, cache_discovery=False)


def edit_insert(service, package_name: str) -> str:
    edit = service.edits().insert(packageName=package_name, body={}).execute()
    return edit["id"]


def edit_commit(service, package_name: str, edit_id: str):
    service.edits().commit(packageName=package_name, editId=edit_id).execute()


# ═════════════════════════════════════════════════════════════════
#  SYNC LISTING
# ═════════════════════════════════════════════════════════════════

def cmd_sync_listing(args):
    app_id = args.app
    dry_run = getattr(args, "dry_run", False)
    config = load_config(app_id)
    package_name = config["packageName"]

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY-RUN: sync-listing --app {app_id}")
        print(f"{'='*60}")
        print(f"[DRY] Paket adı: {package_name}")
        print(f"[DRY] Service Account: {resolve_service_account_path(config)}")
        print(f"[DRY] Varsayılan dil: {config.get('defaultLanguage', 'tr-TR')}")
    else:
        service = get_service(config)
        edit_id = edit_insert(service, package_name)
        print(f"[INFO] Edit oluşturuldu: {edit_id}")

    # 1) Details sync
    if dry_run:
        details = config.get("details", {})
        if details:
            print(f"\n[DRY] Details güncellenecek:")
            for k, v in details.items():
                print(f"       {k}: {v}")
    else:
        sync_details(service, package_name, edit_id, config)

    # 2) Listing (metinler) + images (görseller) sync – her dil için
    metadata_dir = APPS_DIR / app_id / "metadata"
    if not metadata_dir.exists():
        print(f"[WARN] metadata/ dizini bulunamadı: {metadata_dir}")
    else:
        for lang_dir in sorted(metadata_dir.iterdir()):
            if not lang_dir.is_dir():
                continue
            lang = lang_dir.name
            if dry_run:
                print(f"\n[DRY] Dil: {lang}")
                for fname in ("title.txt", "short_description.txt", "full_description.txt"):
                    fpath = lang_dir / fname
                    if fpath.exists():
                        content = fpath.read_text(encoding="utf-8").strip()
                        print(f"       {fname}: {len(content)} karakter → '{content[:50]}{'...' if len(content)>50 else ''}'")
                    else:
                        print(f"       {fname}: BULUNAMADI")
                images_dir = lang_dir / "images"
                if images_dir.exists():
                    for img_type in IMAGE_TYPES.values():
                        folder = images_dir / img_type
                        if folder.exists():
                            files = [f.name for f in folder.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")]
                            if files:
                                print(f"       {img_type}: {len(files)} dosya → {files}")
                        else:
                            print(f"       {img_type}: klasör yok")
            else:
                sync_listing_texts(service, package_name, edit_id, lang, lang_dir)
                sync_images(service, package_name, edit_id, lang, lang_dir)

    if dry_run:
        print(f"\n[DRY] Edit oluşturulacak → tüm yukarıdaki işlemler yapılacak → edit commit edilecek")
        print(f"[DRY] GERÇEK API ÇAĞRISI YAPILMADI.")
        print(f"{'='*60}\n")
    else:
        edit_commit(service, package_name, edit_id)
        print(f"[OK]  Sync tamamlandı ve commit edildi.")


def sync_details(service, package_name: str, edit_id: str, config: dict):
    details = config.get("details", {})
    if not details:
        print("[SKIP] 'details' config'te tanımlı değil.")
        return
    body = {
        "defaultLanguage": details.get("defaultLanguage", config.get("defaultLanguage", "tr-TR")),
        "contactEmail": details.get("contactEmail", ""),
        "contactWebsite": details.get("contactWebsite", ""),
        "contactPhone": details.get("contactPhone", ""),
    }
    # Boş değerleri temizle (API hata verebilir)
    body = {k: v for k, v in body.items() if v}
    if not body:
        print("[SKIP] Details içeriği boş.")
        return
    try:
        service.edits().details().update(
            packageName=package_name, editId=edit_id, body=body
        ).execute()
        print(f"[OK]  Details güncellendi: {body}")
    except HttpError as e:
        print(f"[WARN] Details güncellenemedi: {e}")


def sync_listing_texts(service, package_name: str, edit_id: str, lang: str, lang_dir: Path):
    title_path = lang_dir / "title.txt"
    short_path = lang_dir / "short_description.txt"
    full_path = lang_dir / "full_description.txt"

    body = {}
    if title_path.exists():
        body["title"] = title_path.read_text(encoding="utf-8").strip()
    if short_path.exists():
        body["shortDescription"] = short_path.read_text(encoding="utf-8").strip()
    if full_path.exists():
        body["fullDescription"] = full_path.read_text(encoding="utf-8").strip()

    if not body:
        print(f"[SKIP] {lang}: Metin dosyası bulunamadı.")
        return

    try:
        service.edits().listings().update(
            packageName=package_name, editId=edit_id, language=lang, body=body
        ).execute()
        print(f"[OK]  Listing güncellendi: {lang} → {list(body.keys())}")
    except HttpError as e:
        print(f"[WARN] Listing güncellenemedi ({lang}): {e}")


def sync_images(service, package_name: str, edit_id: str, lang: str, lang_dir: Path):
    images_dir = lang_dir / "images"
    if not images_dir.exists():
        return

    for api_type, folder_name in IMAGE_TYPES.items():
        folder = images_dir / folder_name
        if not folder.exists():
            continue

        # Mevcut görselleri sil (üst üste binmemesi için)
        try:
            service.edits().images().deleteall(
                packageName=package_name, editId=edit_id, language=lang, imageType=api_type
            ).execute()
        except HttpError:
            pass  # Zaten boş olabilir

        files = sorted([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg")])
        if not files:
            continue

        for f in files:
            try:
                media = MediaFileUpload(str(f), mimetype="image/png" if f.suffix == ".png" else "image/jpeg")
                service.edits().images().upload(
                    packageName=package_name,
                    editId=edit_id,
                    language=lang,
                    imageType=api_type,
                    media_body=media,
                ).execute()
                print(f"[OK]  Görsel yüklendi: {lang}/{api_type}/{f.name}")
            except HttpError as e:
                print(f"[WARN] Görsel yüklenemedi ({lang}/{api_type}/{f.name}): {e}")


# ═════════════════════════════════════════════════════════════════
#  RELEASE (AAB upload + track)
# ═════════════════════════════════════════════════════════════════

def cmd_release(args):
    app_id = args.app
    aab_path = Path(args.aab)
    dry_run = getattr(args, "dry_run", False)

    if not aab_path.exists():
        print(f"[HATA] AAB bulunamadı: {aab_path}")
        sys.exit(1)

    config = load_config(app_id)
    package_name = config["packageName"]
    track = config.get("track", "internal")
    release_notes = config.get("releaseNotes", [])

    if dry_run:
        print(f"\n{'='*60}")
        print(f"DRY-RUN: release --app {app_id} --aab {aab_path}")
        print(f"{'='*60}")
        print(f"[DRY] Paket adı: {package_name}")
        print(f"[DRY] Track: {track}")
        print(f"[DRY] AAB boyutu: {aab_path.stat().st_size:,} byte")
        print(f"[DRY] Release notes:")
        for rn in release_notes:
            print(f"       [{rn.get('language')}] {rn.get('text')}")
        print(f"\n[DRY] Edit oluşturulacak → AAB upload edilecek → track '{track}' güncellenecek → commit")
        print(f"[DRY] GERÇEK API ÇAĞRISI YAPILMADI.")
        print(f"{'='*60}\n")
        return

    service = get_service(config)
    edit_id = edit_insert(service, package_name)
    print(f"[INFO] Edit oluşturuldu: {edit_id}")

    # AAB upload
    media = MediaFileUpload(str(aab_path), mimetype="application/octet-stream", resumable=True)
    bundle = service.edits().bundles().upload(
        packageName=package_name, editId=edit_id, media_body=media
    ).execute(num_retries=3)
    version_code = bundle["versionCode"]
    print(f"[OK]  AAB yüklendi — versionCode: {version_code}")

    # Track release notes
    if not release_notes:
        release_notes = [
            {"language": config.get("defaultLanguage", "tr-TR"), "text": "Genel iyileştirmeler ve performans güncellemeleri."},
        ]

    track_body = {
        "track": track,
        "releases": [{
            "versionCodes": [str(version_code)],
            "status": "completed",
            "releaseNotes": release_notes,
        }]
    }
    service.edits().tracks().update(
        packageName=package_name, editId=edit_id, track=track, body=track_body
    ).execute(num_retries=3)
    print(f"[OK]  Track güncellendi: {track}")

    edit_commit(service, package_name, edit_id)
    print(f"[OK]  Release tamamlandı ve commit edildi!")


# ═════════════════════════════════════════════════════════════════
#  SCAFFOLD (yeni app template)
# ═════════════════════════════════════════════════════════════════

def cmd_scaffold(args):
    app_id = args.app
    package = args.package
    title = args.title or app_id.replace("-", " ").title()
    lang = args.lang or "tr-TR"

    app_dir = APPS_DIR / app_id
    if app_dir.exists():
        print(f"[HATA] '{app_id}' zaten mevcut: {app_dir}")
        sys.exit(1)

    # Dizinleri oluştur
    dirs = [
        app_dir / "metadata" / lang / "images" / "phoneScreenshots",
        app_dir / "metadata" / lang / "images" / "sevenInchScreenshots",
        app_dir / "metadata" / lang / "images" / "tenInchScreenshots",
    ]
    for d in dirs:
        d.mkdir(parents=True)

    # config.json
    config = {
        "packageName": package,
        "serviceAccount": "",
        "track": "internal",
        "defaultLanguage": lang,
        "details": {
            "defaultLanguage": lang,
            "contactEmail": "",
            "contactWebsite": "",
            "contactPhone": "",
        },
        "releaseNotes": [
            {"language": lang, "text": "İlk sürüm."},
            {"language": "en-US", "text": "Initial release."},
        ]
    }
    with open(app_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # Metadata metin dosyaları
    (app_dir / "metadata" / lang / "title.txt").write_text(title, encoding="utf-8")
    (app_dir / "metadata" / lang / "short_description.txt").write_text("", encoding="utf-8")
    (app_dir / "metadata" / lang / "full_description.txt").write_text("", encoding="utf-8")

    # README stub
    (app_dir / "README.md").write_text(
        f"# {title}\n\nPaket: `{package}`\n\n" +
        "## Gerekli Adımlar\n\n" +
        "1. `config.json` içinde `serviceAccount` yolunu doldur.\n" +
        "2. Görselleri `metadata/<lang>/images/` altına yerleştir.\n" +
        "3. Mağaza metinlerini `title.txt`, `short_description.txt`, `full_description.txt` dosyalarına yaz.\n" +
        "4. Play Console'dan içerik derecelendirmesi ve gizlilik politikasını manuel tamamla.\n",
        encoding="utf-8"
    )

    print(f"[OK]  Template oluşturuldu: {app_dir}")
    print(f"      Sonraki adımlar için {app_dir}/README.md'yi oku.")


# ═════════════════════════════════════════════════════════════════
#  VALIDATE
# ═════════════════════════════════════════════════════════════════

def cmd_validate(args):
    app_id = args.app
    config = load_config(app_id)
    errors = []
    warnings = []

    metadata_dir = APPS_DIR / app_id / "metadata"
    if not metadata_dir.exists():
        errors.append("metadata/ dizini bulunamadı.")
    else:
        for lang_dir in metadata_dir.iterdir():
            if not lang_dir.is_dir():
                continue
            lang = lang_dir.name

            # Metin uzunlukları
            for field, max_len in MAX_LENGTHS.items():
                txt_path = lang_dir / f"{field}.txt"
                if not txt_path.exists():
                    if field == "title":
                        errors.append(f"{lang}/{field}.txt eksik!")
                    continue
                content = txt_path.read_text(encoding="utf-8").strip()
                if len(content) > max_len:
                    errors.append(f"{lang}/{field}.txt: {len(content)} karakter (max {max_len})")
                if field == "title" and not content:
                    errors.append(f"{lang}/title.txt boş!")

            # Görsel kontrolleri
            images_dir = lang_dir / "images"
            if images_dir.exists():
                icon = images_dir / "icon" / "icon.png"
                if not icon.exists():
                    warnings.append(f"{lang}/images/icon/icon.png eksik (zorunlu)")

                for shot_type in ("phoneScreenshots", "sevenInchScreenshots", "tenInchScreenshots"):
                    folder = images_dir / shot_type
                    if folder.exists():
                        count = len([f for f in folder.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg")])
                        if shot_type == "phoneScreenshots" and count < 2:
                            warnings.append(f"{lang}/images/{shot_type}: en az 2 ekran görüntüsü gerekli ({count} bulundu)")

    # Config kontrolü
    if not config.get("serviceAccount"):
        errors.append("config.json: 'serviceAccount' tanımlı değil.")
    if not config.get("packageName"):
        errors.append("config.json: 'packageName' tanımlı değil.")

    # Özet
    print(f"\n{'='*50}")
    print(f"VALIDATE: {app_id}")
    print(f"{'='*50}")
    if errors:
        print(f"\n❌ HATALAR ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    if warnings:
        print(f"\n⚠️  UYARILAR ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
    if not errors and not warnings:
        print("\n✅ Her şey yolunda.")
    print(f"{'='*50}\n")

    sys.exit(1 if errors else 0)


# ═════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="play-cli.py",
        description="Google Play Store API CLI – Store listing, release ve scaffolding aracı.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sync-listing
    p_sync = sub.add_parser("sync-listing", help="Store listing, details ve images'i API ile senkronize et")
    p_sync.add_argument("--app", required=True, help="App ID (apps/ altındaki klasör adı)")
    p_sync.add_argument("--dry-run", action="store_true", help="API çağrısı yapmadan sadece ne yapılacağını göster")

    # release
    p_rel = sub.add_parser("release", help="AAB upload + track assignment")
    p_rel.add_argument("--app", required=True, help="App ID")
    p_rel.add_argument("--aab", required=True, help="AAB dosyasının yolu")
    p_rel.add_argument("--dry-run", action="store_true", help="API çağrısı yapmadan sadece ne yapılacağını göster")

    # scaffold
    p_sca = sub.add_parser("scaffold", help="Yeni app için template klasörü oluştur")
    p_sca.add_argument("--app", required=True, help="App ID (örn. super-oyun)")
    p_sca.add_argument("--package", required=True, help="Paket adı (örn. com.akn.superoyun)")
    p_sca.add_argument("--title", default=None, help="Uygulama başlığı")
    p_sca.add_argument("--lang", default="tr-TR", help="Varsayılan dil (default: tr-TR)")

    # validate
    p_val = sub.add_parser("validate", help="Metin uzunlukları ve görsel boyutlarını kontrol et")
    p_val.add_argument("--app", required=True, help="App ID")

    args = parser.parse_args()

    if args.command == "sync-listing":
        cmd_sync_listing(args)
    elif args.command == "release":
        cmd_release(args)
    elif args.command == "scaffold":
        cmd_scaffold(args)
    elif args.command == "validate":
        cmd_validate(args)


if __name__ == "__main__":
    main()
