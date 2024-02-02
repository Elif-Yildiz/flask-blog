import os
from dotenv import load_dotenv
from pathlib import Path


class Config:
    current_dir = Path(__file__).resolve().parent
    dotenv_path = current_dir / 'allyouneed.env'
    load_dotenv(dotenv_path)

    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
