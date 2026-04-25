#!/usr/bin/env python3
"""
Google Play Developer API (Edits API) ile dahili test kanalına otomatik yükleme.

Kullanım:
    python3 upload-to-play-store.py --aab app/build/outputs/bundle/release/app-release.aab
    python3 upload-to-play-store.py --apk app/build/outputs/apk/release/app-release.apk

Gereksinimler:
    pip install google-api-python-client google-auth-httplib2

Google Cloud / Play Console Ayarları:
    1. Google Cloud Console -> IAM & Admin -> Service Accounts -> Create
    2. Keys -> Add Key -> JSON (indir)
    3. Google Play Console -> Users & Permissions -> Invite User (service account email)
    4. Rol: "Release Manager" veya "Admin"

API referansı: https://developers.google.com/android-publisher
"""

import argparse
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]
API_SERVICE_NAME = "androidpublisher"
API_VERSION = "v3"


def get_credentials(service_account_file: str):
    """Servis hesabı JSON key'den credentials oluştur."""
    return service_account.Credentials.from_service_account_file(
        service_account_file, scopes=SCOPES
    )


def upload_bundle(service, edit_id: str, package_name: str, aab_path: str) -> dict:
    """.aab dosyasını yükle ve bundle response döndür."""
    media = MediaFileUpload(
        aab_path,
        mimetype="application/octet-stream",
        resumable=True,
    )
    response = (
        service.edits()
        .bundles()
        .upload(editId=edit_id, packageName=package_name, media_body=media)
        .execute()
    )
    return response


def upload_apk(service, edit_id: str, package_name: str, apk_path: str) -> dict:
    """.apk dosyasını yükle ve apk response döndür."""
    media = MediaFileUpload(
        apk_path,
        mimetype="application/vnd.android.package-archive",
        resumable=True,
    )
    response = (
        service.edits()
        .apks()
        .upload(editId=edit_id, packageName=package_name, media_body=media)
        .execute()
    )
    return response


def assign_track(
    service,
    edit_id: str,
    package_name: str,
    track: str,
    version_codes: list[int],
    release_notes: list[dict] | None = None,
    status: str = "completed",
) -> dict:
    """Yüklenen sürümü belirtilen track'e ata."""
    release = {
        "versionCodes": [str(vc) for vc in version_codes],
        "status": status,
    }
    if release_notes:
        release["releaseNotes"] = release_notes

    track_body = {"releases": [release]}

    response = (
        service.edits()
        .tracks()
        .update(
            editId=edit_id,
            track=track,
            packageName=package_name,
            body=track_body,
        )
        .execute()
    )
    return response


def main():
    parser = argparse.ArgumentParser(
        description="Google Play Developer API ile otomatik yükleme"
    )
    parser.add_argument(
        "--package-name",
        default="com.akn.mathlock.play",
        help="Uygulama package name (default: com.akn.mathlock.play)",
    )
    parser.add_argument(
        "--aab",
        help="Yüklenecek .aab dosyasının yolu",
    )
    parser.add_argument(
        "--apk",
        help="Yüklenecek .apk dosyasının yolu",
    )
    parser.add_argument(
        "--service-account",
        default="backend/google-service-account.json",
        help="Servis hesabı JSON key dosyası",
    )
    parser.add_argument(
        "--track",
        default="internal",
        choices=["internal", "alpha", "beta", "production"],
        help="Yayın kanalı (default: internal)",
    )
    parser.add_argument(
        "--status",
        default="completed",
        choices=["draft", "inProgress", "halted", "completed"],
        help="Sürüm durumu (default: completed). Dahili test için 'completed' önerilir.",
    )
    parser.add_argument(
        "--release-name",
        default="",
        help="Sürüm adı (opsiyonel)",
    )

    args = parser.parse_args()

    # Dosya kontrolleri
    if not args.aab and not args.apk:
        print("❌ Hata: --aab veya --apk parametresi gereklidir.", file=sys.stderr)
        sys.exit(1)

    sa_path = Path(args.service_account)
    if not sa_path.exists():
        # Proje root'undan relative path dene
        sa_path = Path("/home/akn/vps/projects/mathlock-play") / args.service_account
    if not sa_path.exists():
        print(f"❌ Hata: Servis hesabı dosyası bulunamadı: {args.service_account}", file=sys.stderr)
        sys.exit(1)

    if args.aab and not Path(args.aab).exists():
        print(f"❌ Hata: AAB dosyası bulunamadı: {args.aab}", file=sys.stderr)
        sys.exit(1)

    if args.apk and not Path(args.apk).exists():
        print(f"❌ Hata: APK dosyası bulunamadı: {args.apk}", file=sys.stderr)
        sys.exit(1)

    # API servisini oluştur
    print(f"🔑 Servis hesabı yükleniyor: {sa_path}")
    credentials = get_credentials(str(sa_path))
    service = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # 1. Edit oluştur
    print(f"📦 Edit oluşturuluyor... (package={args.package_name})")
    edit_response = (
        service.edits().insert(body={}, packageName=args.package_name).execute()
    )
    edit_id = edit_response["id"]
    print(f"   Edit ID: {edit_id}")

    version_codes = []

    # 2. AAB yükle
    if args.aab:
        print(f"📤 AAB yükleniyor: {args.aab}")
        bundle_resp = upload_bundle(service, edit_id, args.package_name, args.aab)
        vc = bundle_resp["versionCode"]
        version_codes.append(vc)
        print(f"   ✓ AAB yüklendi — versionCode: {vc}")

    # 3. APK yükle
    if args.apk:
        print(f"📤 APK yükleniyor: {args.apk}")
        apk_resp = upload_apk(service, edit_id, args.package_name, args.apk)
        vc = apk_resp["versionCode"]
        version_codes.append(vc)
        print(f"   ✓ APK yüklendi — versionCode: {vc}")

    # 4. Track'e ata
    print(f"🚀 Track güncelleniyor: {args.track} (status={args.status})")
    release_notes = None
    if args.release_name:
        release_notes = [
            {
                "language": "tr-TR",
                "text": args.release_name,
            }
        ]

    track_resp = assign_track(
        service,
        edit_id,
        args.package_name,
        args.track,
        version_codes,
        release_notes=release_notes,
        status=args.status,
    )
    print(f"   ✓ Track güncellendi: {track_resp.get('track', args.track)}")

    # 5. Commit
    print("💾 Commit ediliyor...")
    commit_resp = (
        service.edits().commit(editId=edit_id, packageName=args.package_name).execute()
    )
    print(f"   ✓ Commit başarılı: {commit_resp.get('id', edit_id)}")

    print(f"\n🎉 Başarılı! Sürüm Google Play {args.track} kanalına yüklendi.")
    print(f"   Package:    {args.package_name}")
    print(f"   VersionCodes: {version_codes}")
    print(f"   Track:      {args.track}")
    print(f"   Status:     {args.status}")
    print(f"   Console:    https://play.google.com/console/u/0/developers")


try:
    main()
except HttpError as e:
    print(f"\n❌ Google Play API Hatası: {e.resp.status} {e.resp.reason}", file=sys.stderr)
    try:
        print(f"   Detay: {e.error_details}", file=sys.stderr)
    except Exception:
        pass
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Beklenmeyen hata: {e}", file=sys.stderr)
    sys.exit(1)
