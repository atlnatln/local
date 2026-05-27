#!/usr/bin/env python3
import sys, os
import httplib2
from google.oauth2 import service_account
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PACKAGE_NAME = "com.akn.mathlock.play"
TRACK = "internal"
SERVICE_ACCOUNT_FILE = "/home/akn/secrets/mathlock-play/google-service-account.json"
RELEASE_NOTES = [
    {"language": "tr-TR", "text": "Sayı Yolculuğu büyük güncelleme: ses efektleri ve müzik, interaktif tutorial, ipucu sistemi, path preview, undo/redo, başarı rozeti, günlük seviye seti, titreşimli geri bildirim ve kredi satın alma entegrasyonu eklendi."},
    {"language": "en-US", "text": "Major Sayi Yolculugu update: sound effects & music, interactive tutorial, hint system, path preview, undo/redo, achievement badges, daily level set, haptic feedback, and in-app credit purchase integration."},
]

def main(aab_path):
    if not os.path.exists(aab_path):
        print(f"[HATA] AAB bulunamadı: {aab_path}")
        sys.exit(1)

    print(f"[INFO] AAB: {aab_path}")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/androidpublisher"],
    )
    http = httplib2.Http(timeout=120)
    auth_http = AuthorizedHttp(creds, http=http)
    service = build("androidpublisher", "v3", http=auth_http)

    edit = service.edits().insert(packageName=PACKAGE_NAME, body={}).execute()
    edit_id = edit["id"]
    print(f"[INFO] Edit ID: {edit_id}")

    media = MediaFileUpload(aab_path, mimetype="application/octet-stream", resumable=True)
    bundle = service.edits().bundles().upload(
        packageName=PACKAGE_NAME, editId=edit_id, media_body=media
    ).execute(num_retries=3)
    version_code = bundle["versionCode"]
    print(f"[OK] AAB yüklendi — versionCode: {version_code}")

    track_body = {
        "track": TRACK,
        "releases": [{
            "versionCodes": [str(version_code)],
            "status": "draft",
            "releaseNotes": RELEASE_NOTES,
        }]
    }
    service.edits().tracks().update(
        packageName=PACKAGE_NAME, editId=edit_id, track=TRACK, body=track_body
    ).execute(num_retries=3)
    print(f"[OK] Track güncellendi: {TRACK}")

    service.edits().commit(packageName=PACKAGE_NAME, editId=edit_id).execute(num_retries=3)
    print(f"[OK] Edit commit edildi!")
    print(f"[INFO] Play Console: https://play.google.com/console")

if __name__ == "__main__":
    aab = sys.argv[1] if len(sys.argv) > 1 else "/home/akn/local/projects/mathlock-play/app/build/outputs/bundle/release/app-release.aab"
    main(aab)
