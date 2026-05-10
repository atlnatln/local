#!/usr/bin/env python3
import sys, os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

PACKAGE_NAME = "com.akn.mathlock.play"
TRACK = "internal"
SERVICE_ACCOUNT_FILE = "/home/akn/secrets/mathlock-play/google-service-account.json"
RELEASE_NOTES = [
    {"language": "tr-TR", "text": "Hata düzeltmeleri ve iyileştirmeler"},
    {"language": "en-US", "text": "Bug fixes and improvements"},
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
    service = build("androidpublisher", "v3", credentials=creds)

    edit = service.edits().insert(packageName=PACKAGE_NAME, body={}).execute()
    edit_id = edit["id"]
    print(f"[INFO] Edit ID: {edit_id}")

    media = MediaFileUpload(aab_path, mimetype="application/octet-stream")
    bundle = service.edits().bundles().upload(
        packageName=PACKAGE_NAME, editId=edit_id, media_body=media
    ).execute()
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
    ).execute()
    print(f"[OK] Track güncellendi: {TRACK}")

    service.edits().commit(packageName=PACKAGE_NAME, editId=edit_id).execute()
    print(f"[OK] Edit commit edildi!")
    print(f"[INFO] Play Console: https://play.google.com/console")

if __name__ == "__main__":
    aab = sys.argv[1] if len(sys.argv) > 1 else "/home/akn/local/projects/mathlock-play/app/build/outputs/bundle/release/app-release.aab"
    main(aab)
