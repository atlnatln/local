import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
AUTHORIZED_USERS = set()
for uid in os.getenv("AUTHORIZED_USERS", "").split(","):
    uid = uid.strip()
    if uid:
        try:
            AUTHORIZED_USERS.add(int(uid))
        except ValueError:
            pass

WORK_DIR = os.getenv("WORK_DIR", "/home/akn/vps")
KIMI_CMD = os.getenv("KIMI_CMD", "kimi")
KIMI_ARGS = os.getenv("KIMI_ARGS", "acp").split()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
PROMPT_TIMEOUT = int(os.getenv("PROMPT_TIMEOUT", "300"))

# Chunk streaming: her N saniyede bir veya M chunk'ta bir Telegram'a gönder
STREAM_CHUNK_INTERVAL = float(os.getenv("STREAM_CHUNK_INTERVAL", "1.5"))
STREAM_MAX_CHUNKS = int(os.getenv("STREAM_MAX_CHUNKS", "20"))

# Local PC SSH reverse tunnel settings
LOCAL_SSH_HOST = os.getenv("LOCAL_SSH_HOST", "localhost")
LOCAL_SSH_PORT = int(os.getenv("LOCAL_SSH_PORT", "9876"))
LOCAL_SSH_USER = os.getenv("LOCAL_SSH_USER", "akn")
LOCAL_SSH_KEY = os.getenv("LOCAL_SSH_KEY", "~/.ssh/id_ed25519_kimibot")
LOCAL_SSH_WORK_DIR = os.getenv("LOCAL_SSH_WORK_DIR", "/home/akn/vps")
