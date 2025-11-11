from ..extentions import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now)