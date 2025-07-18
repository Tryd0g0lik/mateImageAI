import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY_DJ = os.getenv("SECRET_KEY_DJ", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
DB_ENGINE = os.getenv("DB_ENGINE", "")

APP_PROTOCOL = os.getenv("APP_PROTOCOL", "")
APP_HOST = os.getenv("APP_HOST", "")
APP_PORT = os.getenv("APP_PORT", "")
# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Email сервис (опционально)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PORT = os.getenv("SMTP_PORT", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


URL_REDIRECT_IF_NOTGET_AUTHENTICATION = os.getenv(
    "URL_REDIRECT_IF_NOTGET_AUTHENTICATION", ""
)
URL_REDIRECT_IF_GET_AUTHENTICATION = os.getenv("URL_REDIRECT_IF_GET_AUTHENTICATION", "")
