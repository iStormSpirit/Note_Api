import os

from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from marshmallow import fields

from api import api
from api.models.file import FileModel
from api.schemas.file import FileSchema
from config import Config, ma_plugin


@ma_plugin.map_to_openapi_type('file', None)
class FileField(fields.Raw):
    pass


@doc(tags=['Files'])
@api.resource('/upload')
class UploadPictureResource(MethodResource):
    @use_kwargs({"image": FileField(required=True)}, location="files")
    @marshal_with(FileSchema, code=201)
    def put(self, **kwargs):
        uploaded_file = kwargs["image"]
        target = os.path.join(Config.UPLOAD_FOLDER, uploaded_file.filename)
        uploaded_file.save(target)
        url = os.path.join(Config.UPLOAD_FOLDER_NAME, uploaded_file.filename)
        file = FileModel(url=url)
        file.save()
        return file, 201
