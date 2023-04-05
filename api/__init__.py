import logging

from flask import Flask, g, request
from flask_apispec.extension import FlaskApiSpec
from flask_babel import Babel
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail, Message
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from config import Config

# Это из документации:
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#using-custom-metadata-and-naming-conventions
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

app = Flask(__name__, static_folder=Config.UPLOAD_FOLDER)
app.config.from_object(Config)

api = Api(app)
db = SQLAlchemy(app, metadata=metadata)

# Про render_as_batch тут: https://alembic.sqlalchemy.org/en/latest/batch.html
# Суть кратко: База данных SQLite представляет собой проблему для инструментов миграции,
# поскольку она почти не поддерживает оператор ALTER
# Команда ALTER TABLE используется для добавления, удаления или модификации колонки в уже существующей таблице
migrate = Migrate(app, db, render_as_batch=True)
ma = Marshmallow(app)
auth = HTTPBasicAuth()
mail = Mail(app)
babel = Babel(app)

docs = FlaskApiSpec(app)
logging.basicConfig(filename='record.log',
                    level=logging.INFO,
                    format=f'%(asctime)s %(levelname)s %(name)s : %(message)s')
app.logger.setLevel(logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.INFO)


@babel.localeselector
def get_locale():
    res = request.accept_languages.best_match(app.config['LANGUAGES'])
    return res


@auth.verify_password
def verify_password(username_or_token, password):
    from api.models.user import UserModel

    # сначала проверяем authentication token
    # print("username_or_token = ", username_or_token)
    # print("password = ", password)
    user = UserModel.verify_auth_token(username_or_token)
    if not user:
        # потом авторизация
        user = UserModel.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@auth.get_user_roles
def get_user_roles(user):
    return g.user.get_roles()
