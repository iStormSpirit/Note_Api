from api import ma
from api.models.file import FileModel


# Сериализация ответа(response)
class FileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FileModel
