from api import auth, abort, g,  reqparse
from api.models.user import UserModel
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.schemas.note import NoteSchema, NoteRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Note'])
class NoteResource(MethodResource):
    @auth.login_required
    @doc(summary="Get Note by id", description='Get note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def get(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        return note, 200

    @auth.login_required
    @doc(summary="Edit Note by id", description='Edit note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    @use_kwargs(NoteRequestSchema, location=('json'))
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=_(f"Forbidden"))
        note.text = kwargs["text"]
        note.private = kwargs["private"]
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Delete Note by id", description='Delete note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def delete(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        note_dict = note
        note.delete()
        return note_dict, 200


@doc(tags=['Note'])
class NotesListResource(MethodResource):
    @auth.login_required
    @doc(summary="Get Note", description='Get all notes', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True))
    def get(self):
        author = g.user
        notes = NoteModel.query.filter_by(author_id=author.id)
        return notes, 200

    @auth.login_required
    @doc(summary="Post Note", description='Create note', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    @use_kwargs(NoteRequestSchema)
    def post(self, **kwargs):
        author = g.user
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201


@doc(tags=['Note'])
class NoteTagsResource(MethodResource):
    @auth.login_required
    @doc(summary="Add tags to Note", description='Add tags to Note', security=[{"basicAuth": []}])
    @use_kwargs({"tags": fields.List(fields.Int())}, location=('json'))
    @marshal_with(NoteSchema)
    def put(self, note_id, **kwargs):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.append(tag)
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Delete tags from Note", description='Delete tags to Note', security=[{"basicAuth": []}])
    @use_kwargs({"tags": fields.List(fields.Int())}, location=('json'))
    @marshal_with(NoteSchema)
    def delete(self, note_id, **kwargs):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.remove(tag)
        note.save()
        return note, 200


@doc(tags=['NotesFilter'])
class NotesPublicResource(MethodResource):
    @doc(summary="Get all public notes", description='Get public notes')
    @marshal_with(NoteSchema(many=True))
    def get(self):
        notes = NoteModel.query.filter_by(private=False)
        return notes, 200


@doc(tags=['NotesFilter'])
class NoteFilterByTagResource(MethodResource):
    @auth.login_required
    @doc(summary="Get notes by tags", description='Filter by tags in note', security=[{"basicAuth": []}])
    @use_kwargs({"tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, **kwargs):
        notes = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
        return notes, 200


@doc(tags=['NotesFilter'])
class NotesFilterByUserResource(MethodResource):
    @doc(summary="Get notes by author", description='Filter by author in note')
    @use_kwargs({"username": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, **kwargs):
        notes = NoteModel.query.filter(UserModel.username.has(username=kwargs['username']))
        return notes, 200
