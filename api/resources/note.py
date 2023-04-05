from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_babel import gettext
from sqlalchemy.orm.exc import NoResultFound
from webargs import fields

from api import abort, api, auth, g
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.schemas.note import (NoteCreateSchema, NoteEditSchema,
                              NoteFilterSchema, NoteFilterTagsSchema,
                              NoteSchema)


@doc(tags=['Note'])
@api.resource('/notes/<int:note_id>')
class NoteResource(MethodResource):
    @auth.login_required
    @doc(summary="Get Note by id", description='Get note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema, code=200)
    def get(self, note_id):
        author = g.user
        try:
            note = NoteModel.get_all_for_user(author).filter_by(id=note_id).one()
            return note, 200
        except NoResultFound:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))

    @auth.login_required
    @doc(summary="Edit Note by id", description='Edit note by id', security=[{"basicAuth": []}])
    @marshal_with(NoteSchema, code=200)
    @use_kwargs(NoteEditSchema, location='json')
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))
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
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))
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
    @marshal_with(NoteSchema, code=201)
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
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))
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
    @use_kwargs({"tags": fields.List(fields.Int())}, location='query')
    @marshal_with(NoteSchema, code=200)
    def put(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if note.author != author:
            abort(403, error=f"Forbidden")
        if not note:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            if not tag:
                abort(404, error=gettext("Tag with id %(tag_id)s not found", tag_id=tag_id))
            note.tags.append(tag)
        note.save()
        return note, 200

    @auth.login_required
    @doc(summary="Delete tags from Note", description='Delete tags to Note', security=[{"basicAuth": []}])
    @use_kwargs({"tags": fields.List(fields.Int())}, location='query')
    @marshal_with(NoteSchema, code=200)
    def delete(self, note_id, **kwargs):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=gettext("Note with id %(note_id)s not found", note_id=note_id))
        if not set(kwargs['tags']) <= set([el.id for el in note.tags]):
            abort(400, error=gettext("List of tag ids not match to note with id %(note_id)s", note_id=note_id))
        if note.author != author:
            abort(403, error=f"Forbidden")
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.remove(tag)
        note.save()
        return note, 200


@doc(tags=['Note extra options'])
@api.resource('/notes/like')
class NoteTexResource(MethodResource):
    @auth.login_required
    @doc(summary="Find notes with text", description='Find notes with text', security=[{"basicAuth": []}])
    @use_kwargs({"text": fields.String(load_default="")}, location='query')
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, text):
        author = g.user
        if text:
            notes = NoteModel.get_all_for_user(author).filter(NoteModel.text.like(f"%{text}%"))
            return notes, 200
        abort(400, error=gettext("Need key to search"))


@doc(tags=['Note extra options'])
@api.resource('/notes/tags')
class NoteFilterTagsResource(MethodResource):
    @auth.login_required
    @doc(summary="Get user's notes by list tag's id",
         description="Get user's notes by list tag's id", security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True), code=200)
    @use_kwargs(NoteFilterTagsSchema, location='query')
    def get(self, **kwargs):
        author = g.user
        notes = NoteModel.get_all_for_user(author)
        if kwargs.get("tags") is not None:
            notes = notes.filter(NoteModel.tags.any(TagModel.id.in_(kwargs['tags']))).all()
            return notes, 200
        abort(400, error=gettext("Need key to search"))
