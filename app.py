from api import api, app, docs
from api.resources.note import NoteResource, NotesListResource, NotesPublicResource, \
    NoteTagsResource, NoteFilterByTagPlusUserResource, NoteFilterByTagResource
from api.resources.user import UserResource, UsersListResource
from api.resources.auth import TokenResource
from api.resources.tag import TagsResource, TagsListResource
from config import Config

api.add_resource(UsersListResource, '/users')  # GET, POST
api.add_resource(UserResource, '/users/<int:user_id>')  # GET, PUT, DELETE

api.add_resource(TokenResource, '/auth/token')  # GET

api.add_resource(NotesListResource, '/notes')  # GET, POST
api.add_resource(NoteResource, '/notes/<int:note_id>')  # GET, PUT, DELETE

api.add_resource(NoteTagsResource, '/notes/<int:note_id>/tags')  # PUT # DELETE

api.add_resource(TagsListResource, '/tags')  # GET, POST
api.add_resource(TagsResource, '/tags/<int:tag_id>')  # GET, PUT, DELETE

api.add_resource(NotesPublicResource, '/notes/public')  # GET All Public Notes or filter by username
api.add_resource(NoteFilterByTagResource, '/notes/filter/tag')  # GET All Public Notes or filter Tags
api.add_resource(NoteFilterByTagPlusUserResource, '/notes/filter')  # GET All Public Notes or Tags and User

docs.register(UserResource)
docs.register(UsersListResource)

docs.register(NoteResource)
docs.register(NotesListResource)

docs.register(NoteTagsResource)

docs.register(TagsResource)
docs.register(TagsListResource)

docs.register(NotesPublicResource)
docs.register(NoteFilterByTagResource)
docs.register(NoteFilterByTagPlusUserResource)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
