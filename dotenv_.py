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

DATABASE_FOR_TEST = os.getenv("DATABASE_FOR_TEST", "")
DATABASE_ENGINE_FOR_TEST = os.getenv("DATABASE_ENGINE_FOR_TEST", "")
DATABASE_ENGINE_FOR_DEFAULT = os.getenv("DATABASE_ENGINE_FOR_DEFAULT", "")
# Redis
REDIS_LOCATION_URL = os.getenv("REDIS_LOCATION_URL", "")
DB_TO_RADIS_CACHE_USERS = os.getenv("DB_TO_RADIS_CACHE_USERS", "")
DB_TO_RADIS_PORT = os.getenv("DB_TO_RADIS_PORT", "")
DB_TO_RADIS_HOST = os.getenv("DB_TO_RADIS_HOST", "")
# CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")

# Email сервис (опционально)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PORT = os.getenv("SMTP_PORT", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


URL_REDIRECT_IF_NOTGET_AUTHENTICATION = os.getenv(
    "URL_REDIRECT_IF_NOTGET_AUTHENTICATION", ""
)
URL_REDIRECT_IF_GET_AUTHENTICATION = os.getenv("URL_REDIRECT_IF_GET_AUTHENTICATION", "")
