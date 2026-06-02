import os


DATABASE_URL = os.environ["DATABASE_URL"]
PORT = int(os.getenv("PORT", "3000"))
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")

