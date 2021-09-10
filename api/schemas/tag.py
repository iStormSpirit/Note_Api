from api import ma
from api.models.tag import TagModel


#       schema        flask-restful
# object ------>  dict ----------> json


# Сериализация ответа(response)
class TagSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TagModel

    id = ma.auto_field()
    name = ma.auto_field()


tag_schema = TagSchema()
tags_schema = TagSchema(many=True)

# # Десериализация запроса(request)
# class UserRequestSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = UserModel
#
#     username = ma.Str()
#     password = ma.Str()
#
#
