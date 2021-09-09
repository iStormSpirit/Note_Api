from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.schemas.note import note_schema, notes_schema, NoteSchema, NoteRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc


@doc(tags=['Note'])
class NoteResource(MethodResource):
    @doc(description='Get note by id')
    @marshal_with(NoteSchema)
    @auth.login_required
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

    @doc(description='Get note by id')
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
    @doc(description='Get all notes')
    @marshal_with(NoteSchema(many=True))
    def get(self):
        notes = NoteModel.query.all()
        return notes, 200

    @auth.login_required
    @doc(description='Create note')
    @marshal_with(NoteSchema)
    def post(self):
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        parser.add_argument("private", type=bool)
        note_data = parser.parse_args()
        note = NoteModel(author_id=author.id, **note_data)
        note.save()
        return note, 201
