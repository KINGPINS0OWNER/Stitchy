from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json  # ✅ Required for json.loads

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    floss_codes = db.Column(db.Text)  # This stores the floss_data as a JSON string
    floss_yardage = db.Column(db.String(50))  # (Optional – not actively used)
    image_filename = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    
    