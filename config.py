# --- config.py ---
import os
from dotenv import load_dotenv

# Load environment variables from .env file located in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # Attempt loading from current directory if .env is alongside config.py (less common)
    load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-unsafe-secret-key-please-change'
    # Add other Flask configuration variables here if needed, e.g.:
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
