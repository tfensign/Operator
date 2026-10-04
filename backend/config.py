import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/operator.db"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

BACKEND_PORT = int(os.getenv("BACKEND_PORT", 3001))
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")

# Security
ENCRYPTION_KEY_LENGTH = 32  # For AES-256
BCRYPT_ROUNDS = 12

# Message auto-purge (days)
MESSAGE_RETENTION_DAYS = 90
