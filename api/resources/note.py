from api import auth, abort, g, Resource, reqparse, api
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.schemas.note import NoteSchema, NoteEditSchema, NoteCreateSchema, NoteFilterSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_babel import _


@doc(tags=['Note'])
@api.resource('/notes/<int:note_id>')
class NoteResource(MethodResource):
    @auth.login_required
    @doc(summary="Get Note by id", description='Get note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def get(self, note_id):
        author = g.user
        try:
            note = NoteModel.get_all_for_user(author).filter_by(id=note_id).one()
            return note, 200
        except NoResultFound:
            abort(404, error=f"Note with id {note_id} not found")

    @auth.login_required
    @doc(summary="Edit Note by id", description='Edit note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    @use_kwargs(NoteEditSchema, location='json')
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        if kwargs.get("text") is not None:
            note.text = kwargs.get("text")
        if kwargs.get("private") is not None:
            note.private = kwargs.get("private")
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Move Note by id to archive", description='Move Note by id to archive', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def delete(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=f"Note with id:{note_id} not found")
        note.archivated()
        return note, 200


@doc(tags=['Note'])
@api.resource('/notes')
class NotesListResource(MethodResource):
    @auth.login_required
    @doc(summary="Get notes list", security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True), code=200)
    @use_kwargs(NoteFilterSchema, location='query')
    def get(self, **kwargs):
        author = g.user
        notes = NoteModel.get_all_for_user(author)
        if kwargs.get('tag') is not None:
            notes = notes.filter(NoteModel.tags.any(name=kwargs['tag']))
        if kwargs.get('private') is not None:
            notes = notes.filter_by(private=kwargs['private'])
        if kwargs.get('username') is not None:
            notes = notes.filter(NoteModel.author.has(username=kwargs['username']))
        return notes, 200

    @auth.login_required
    @doc(summary="Post Note", description='Create note', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    @use_kwargs(NoteCreateSchema)
    def post(self, **kwargs):
        author = g.user
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201


@doc(tags=['Note extra options'])
@api.resource('/notes/<int:note_id>/restore')
class NoteRestoreResource(MethodResource):
    @auth.login_required
    @doc(summary="back notes from archive", description='back notes from archive', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema)
    def put(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Not found note with id {note_id}")
        if not note.archive:
            return {}, 304
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.restore()
        return note, 200


@doc(tags=['Note extra options'])
@api.resource('/notes/<int:note_id>/tags')
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


@doc(tags=['Note extra options'])
@api.resource('/notes/like')
class NoteTexResource(MethodResource):
    @auth.login_required
    @doc(summary="Find notes with text", description='Find notes with text', security=[{"basicAuth": []}])
    @use_kwargs({"text": fields.String(load_default="")}, location='query')
    @marshal_with(NoteSchema(many=True))
    def get(self, text):
        author = g.user
        if text:
            notes = NoteModel.get_all_for_user(author).filter(NoteModel.text.like(f"%{text}%"))
            return notes, 200
        abort(404, error=f"Need key to search")

# TODO поиск по списку тегов
