from api import ma
from api.models.user import UserModel
from api.schemas.file import FileSchema


#       schema        flask-restful
# object ------>  dict ----------> json


# Сериализация ответа(response)
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel
        # fields = ('id', 'username', 'is_staff', 'role')

    id = ma.auto_field()
    username = ma.auto_field()
    is_staff = ma.auto_field()
    role = ma.auto_field()
    photo = ma.Nested(FileSchema())
    # photo_url = ma.auto_field()

    _links = ma.Hyperlinks({
        'self': ma.URLFor('userresource', values=dict(user_id="<id>")),
        'collection': ma.URLFor('userslistresource')
    })


# Десериализация запроса(request)
class UserCreateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    username = ma.Str()
    password = ma.Str()
    photo_id = ma.Integer(required=False)
    # photo_url = ma.Str(required=False)


class UserEditSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    username = ma.Str(required=False)
    photo_id = ma.Integer(required=False)
