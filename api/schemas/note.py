from api import ma
from api.models.note import NoteModel
from api.schemas.tag import TagSchema
from api.schemas.user import UserSchema

#       schema        flask-restful
# object ------>  dict ----------> json

class NoteSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel

    id = ma.auto_field()
    text = ma.auto_field()
    private = ma.auto_field()
    archive = ma.auto_field()
    author = ma.Nested(UserSchema())
    tags = ma.Nested(TagSchema(many=True))

    _links = ma.Hyperlinks({
        'self': ma.URLFor('noteresource', values=dict(note_id="<id>")),
        'collection': ma.URLFor('noteslistresource')
    })


class NoteCreateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel
        fields = ['text', 'private']

    text = ma.auto_field()
    private = ma.auto_field()


class NoteEditSchema(ma.SQLAlchemySchema):
    class Meta:
        model = NoteModel

    text = ma.auto_field(required=False)
    private = ma.auto_field(required=False)


class NoteFilterSchema(ma.SQLAlchemySchema):
    private = ma.Bool(required=False)
    tag = ma.String(required=False)
    username = ma.Str(required=False)


class NoteFilterTagsSchema(ma.SQLAlchemySchema):
    private = ma.Boolean(required=False)
    tags = ma.List(ma.String())
