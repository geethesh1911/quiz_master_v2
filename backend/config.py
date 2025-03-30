import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///quizmaster.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5000')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '23f2003015@ds.study.iitm.ac.in')
    broker_connection_retry_on_startup = True

    