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
