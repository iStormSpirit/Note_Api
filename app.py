from api import api, app, docs
from api.resources.note import NoteResource, NotesListResource, NotesPublicResource, \
    NoteTagsResource, NoteFilterByTagResource
from api.resources.user import UserResource, UsersListResource
from api.resources.auth import TokenResource
from api.resources.tag import TagsResource, TagsListResource
from config import Config

api.add_resource(UsersListResource, '/users')  # GET, POST
api.add_resource(UserResource, '/users/<int:user_id>')  # GET, PUT, DELETE
api.add_resource(TokenResource, '/auth/token')  # GET

api.add_resource(NotesListResource, '/notes')  # GET, POST
api.add_resource(NoteResource, '/notes/<int:note_id>')  # GET, PUT, DELETE
api.add_resource(NotesPublicResource, '/notes/public')  # GET Public Notes

api.add_resource(NoteTagsResource, '/notes/<int:note_id>/tags')  # PUT # DELETE

api.add_resource(TagsListResource, '/tags')  # GET, POST
api.add_resource(TagsResource, '/tags/<int:tag_id>')  # GET, PUT, DELETE

api.add_resource(NoteFilterByTagResource, '/notes/filter')  # GET by Tags
# api.add_resource(NotesFilterByUserResource, '/notes/public/filter')  # GET by User

# api.add_resource(NotesStatusResource, '/notes/<int:note_id>/status/<int:note_id>')
# docs.register(NotesStatusResource)

docs.register(UserResource)
docs.register(UsersListResource)

docs.register(NoteResource)
docs.register(NotesListResource)
docs.register(NotesPublicResource)

docs.register(NoteTagsResource)

docs.register(TagsResource)
docs.register(TagsListResource)

docs.register(NoteFilterByTagResource)
# docs.register(NotesFilterByUserResource)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
