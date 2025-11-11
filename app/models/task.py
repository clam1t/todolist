from ..extentions import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    deadline = db.Column(db.DateTime, default=datetime.now)
    is_done = db.Column(db.Boolean, default=False)