from api import db, Config, ma
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import expression
from api.models.file import FileModel


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('NoteModel', backref='author', lazy='dynamic')
    is_staff = db.Column(db.Boolean(), default=False, server_default=expression.true(), nullable=False)
    role = db.Column(db.String(32), default=False, server_default=expression.true(), nullable=False)
    photo_id = db.Column(db.Integer, db.ForeignKey("file_model.id"), nullable=True)
    photo = db.relationship(FileModel, backref="user", lazy='joined')
    # photo_url = db.Column(db.String(128))

    def __init__(self, **kwargs):
        password = kwargs["password"]
        del kwargs["password"]
        super().__init__(**kwargs)
        self.hash_password(password)
    # def __init__(self, username, password):
    #     self.username = username
    #     self.hash_password(password)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(Config.SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    def get_roles(self):
        return self.role

    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError:
            print(f"User with username={self.username} already exist")
            db.session.rollback()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = UserModel.query.get(data['id'])
        return user

    def __repr__(self):
        return f"User {self.username}, role:{self.role}"
