import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'data', 'db.sqlite3')}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "dev-secret"
