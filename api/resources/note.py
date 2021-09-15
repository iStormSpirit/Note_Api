from api import auth, abort, g
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
    # @doc(summary="Delete Note by id", description='Delete note by id', security=[{"basicAuth": []}])
    @doc(summary="Move Note by id to archive", description='Move Note by id to archive', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def delete(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        note.delete()
        return note, 200


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

    # FIXME почему в консоли появляется предупреждение?
    #  /home/boo/Projects/Flask2/NoteApi/note_venv/lib/python3.8/site-packages/apispec/ext/marshmallow/common.py:127:
    #  UserWarning: Multiple schemas resolved to the name Generated. The name has been modified.
    #  Either manually add each of the schemas with a different name or provide a custom schema_name_resolver. warnings.warn(
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
            note.tags.delete(tag)
        note.save()
        return note, 200


@doc(tags=['NotesFilter'])
class NotesFilterByTagResource(MethodResource):
    @auth.login_required
    @doc(summary="Get all notes by tags", description='Get all notes by tags', security=[{"basicAuth": []}])
    @use_kwargs({"tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, **kwargs):
        notes = NoteModel.query.all()
        if kwargs:
            notes = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
            return notes, 200
        return notes, 200


# FIXME: добавить возможность фильтрации только по тегу,
#  а так же возможность фильтрации с приватность (публичные/приватные/все)
@doc(tags=['NotesFilter'])
class NoteFilterResource(MethodResource):
    @doc(summary="Get all public notes + filter's",
         description='Get all public notes + filter by username/ username + tag')
    @use_kwargs({"username": fields.Str(), "tag": fields.Str()}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, **kwargs):
        notes = NoteModel.query.filter_by(archive=False)
        if "username" and "tag" in kwargs:
            notes_tags = NoteModel.query.filter(NoteModel.tags.any(name=kwargs["tag"]))
            notes_user = notes_tags.filter(NoteModel.author.has(username=kwargs["username"]))
            notes = notes_user.filter_by(archive=False)
            return notes, 200
        if "username" in kwargs:
            notes_user = NoteModel.query.filter(NoteModel.author.has(username=kwargs["username"]))
            notes = notes_user.filter_by(archive=False)
            return notes, 200
        return notes, 200


# FIXME как вывести ошибку если ключ поиска в заметках не найден
@doc(tags=['NotesFilter'])
class NoteTexResource(MethodResource):
    @doc(summary="Find notes with text",
         description='Find notes with text')
    @use_kwargs({"text": fields.String(load_default="")}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, text):
        if text:
            notes = NoteModel.query.filter(NoteModel.text.like(f"%{text}%"))
            return notes, 200
        abort(404, error=f"Need key to search")


@doc(tags=['Note'])
class NoteRestoreResource(MethodResource):
    # '/notes/<int:note_id>/restore'
    @doc(summary="back notes from archive", description='back notes from archive')
    @marshal_with(NoteSchema)
    def put(self, note_id):
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Not found note with id {note_id}")
        if not note.archive:
            return {}, 304
        note.restore()
        return note, 200
