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


# Десериализация запроса(request)
# class TagRequestSchema(ma.SQLAlchemySchema):
#     class Meta:
#         model = TagModel
#
#     name = ma.Str()
#

tag_schema = TagSchema()
tags_schema = TagSchema(many=True)
