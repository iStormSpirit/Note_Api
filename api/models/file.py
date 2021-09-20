from api import db
from sqlalchemy.sql import expression


class FileModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), unique=True, nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()