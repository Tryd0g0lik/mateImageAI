import os

import dotenv

dotenv.load_dotenv()

SECRET_KEY_DJ = os.getenv("SECRET_KEY_DJ", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
ALCHEMY_DATABASE_URL = "postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DB_ENGINE = os.getenv("DB_ENGINE", "")

# База данных
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Email сервис (опционально)
# EMAIL_SERVICE_API_KEY=
