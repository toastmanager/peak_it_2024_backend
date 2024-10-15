import os

from dotenv import load_dotenv

load_dotenv()

DB_USER = f"{os.environ.get("DB_USER")}"
DB_NAME = f"{os.environ.get("DB_NAME")}"
DB_PASS = f"{os.environ.get("DB_PASS")}"
DB_HOST = f"{os.environ.get("DB_HOST")}"
DB_PORT = f"{os.environ.get("DB_PORT")}"

SECRET = f"{os.environ.get("SECRET")}"