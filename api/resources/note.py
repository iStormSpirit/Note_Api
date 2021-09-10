from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.schemas.note import note_schema, notes_schema, NoteSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc


@doc(tags=['Note'])
class NoteResource(MethodResource):
    @doc(description='Get note by id')
    @marshal_with(NoteSchema)
    @auth.login_required
    @doc(security=[{"basicAuth": []}])
    def get(self, note_id):
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        return note, 200

    @auth.login_required
    @doc(description='Edit note by id')
    @marshal_with(NoteSchema)
    @doc(security=[{"basicAuth": []}])
    def put(self, note_id):
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        parser.add_argument("private", type=bool)
        note_data = parser.parse_args()
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.text = note_data["text"]
        note.private = note_data.get("private") or note.private
        note.save()
        return note, 200

    @doc(description='Delete note by id')
    @marshal_with(NoteSchema)
    @doc(security=[{"basicAuth": []}])
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
    @doc(description='Get all notes')
    @doc(security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True))
    def get(self):
        author = g.user
        notes = NoteModel.query.filter_by(author_id=author.id)
        return notes, 200

    @auth.login_required
    @doc(description='Create note')
    @marshal_with(NoteSchema)
    @doc(security=[{"basicAuth": []}])
    def post(self):
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        parser.add_argument("private", type=bool)
        note_data = parser.parse_args()
        note = NoteModel(author_id=author.id, **note_data)
        note.save()
        return note, 201


@doc(tags=['Notes'])
class NotesPublicResource(MethodResource):
    @marshal_with(NoteSchema(many=True))
    @doc(description='Get public notes')
    def get(self):
        notes = NoteModel.query.filter_by(private=False)
        return notes, 200
