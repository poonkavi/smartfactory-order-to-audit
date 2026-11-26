import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-later")
    SQLALCHEMY_DATABASE_URI = "sqlite:///smartfactory.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    