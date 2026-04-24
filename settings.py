import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # EMAIL
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    # DATABASE
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    # API KEYS
    FRED_API_KEY = os.getenv("FRED_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # RECIPIENTS (convert string → list)
    RECIPIENTS = os.getenv("RECIPIENTS", "").split(",")


settings = Settings()