from api import auth, abort, g
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
    @use_kwargs(NoteRequestSchema, location='json')
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"note {note_id} not found")
        note.text = kwargs["text"]
        note.private = kwargs["private"]
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Delete Note by id", description='Delete note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def delete(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        note_dict = note
        note.delete()
        return note_dict, 200


@doc(tags=['Note'])
class NotesListResource(MethodResource):
    @auth.login_required
    @doc(summary="Get Note", description='Get all notes')
    @marshal_with(NoteSchema(many=True))
    @doc(security=[{"basicAuth": []}])
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
    @use_kwargs({"tags": fields.List(fields.Int())}, location='json')
    @marshal_with(NoteSchema)
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"note {note_id} not found")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if not tag:
                abort(404, error=f"tag {tag_id} not found")
            note.tags.append(tag)
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Delete tags from Note", description='Delete tags to Note', security=[{"basicAuth": []}])
    @use_kwargs({"tags": fields.List(fields.Int())}, location='json')
    @marshal_with(NoteSchema)
    def delete(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"note {note_id} not found")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if not note.tags:
                abort(404, error=f"tag {tag_id} in note {note_id} not found")
            note.tags.remove(tag)
        note.save()
        return note, 200


@doc(tags=['NotesPublicFilter'])
class NoteFilterResource(MethodResource):
    @doc(summary="Get all public notes + filter's",
         description='Get all public notes + filter by username/ username + tag')
    @use_kwargs({"username": fields.Str(), "tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, **kwargs):
        notes = NoteModel.query.filter_by(private=False)
        if "username" and "tag" in kwargs:
            notes_tags = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
            notes_public = notes_tags.filter_by(private=False)
            notes_user = notes_public.filter(NoteModel.author.has(username=kwargs["username"]))
            return notes_user, 200
        if "username" in kwargs:
            notes_user = NoteModel.query.filter(NoteModel.author.has(username=kwargs["username"]))
            notes_public = notes_user.filter_by(private=False)
            return notes_public, 200
        if "tag" in kwargs:
            notes_tags = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
            notes_public_tag = notes_tags.filter_by(private=False)
            return notes_public_tag, 200
        return notes, 200


@doc(tags=['NotesPublicFilter'])
class NotesFilterByTagResource(MethodResource):
    @auth.login_required
    @doc(summary="Get all public notes + filter by tags", description='Filter all public + filter by tags')
    @use_kwargs({"tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True))
    @doc(security=[{"basicAuth": []}])
    def get(self, **kwargs):
        notes = NoteModel.query.filter_by(private=False)
        if kwargs:
            notes_t = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
            notes_public_tag = notes_t.filter_by(private=False)
            return notes_public_tag, 200
        return notes, 200
