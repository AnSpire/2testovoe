import os
from datetime import timedelta

# В реальном проекте секрет задаётся только через окружение.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me-please-32-bytes!")
ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(minutes=int(os.getenv("JWT_TTL_MINUTES", "30")))
