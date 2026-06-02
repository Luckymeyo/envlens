import os


DATABASE_URL = os.environ["DATABASE_URL"]
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
APP_ENV = os.getenv("APP_ENV", "development")

