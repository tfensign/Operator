import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create data directory: {e}")
    print(f"DATA_DIR: {DATA_DIR}")

DATABASE_URL = f"sqlite:///{DATA_DIR}/operator.db"

BACKEND_PORT = int(os.getenv("PORT") or os.getenv("BACKEND_PORT", 8000))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")

# Security
ENCRYPTION_KEY_LENGTH = 32  # For AES-256
BCRYPT_ROUNDS = 12

# Message auto-purge (days)
MESSAGE_RETENTION_DAYS = 90
