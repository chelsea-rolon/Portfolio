from datetime import datetime

from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    details = db.Column(db.String(300), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"Task('{self.title}', '{self.date}')"