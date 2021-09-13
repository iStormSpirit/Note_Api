from api import api, app, docs
from api.resources.note import NoteResource, NotesListResource, NoteTagsResource, \
    NoteFilterResource, NotesFilterByTagResource
from api.resources.user import UserResource, UsersListResource
from api.resources.auth import TokenResource
from api.resources.tag import TagsResource, TagsListResource
from config import Config

# TODO сделано
api.add_resource(UsersListResource, '/users')  # GET, POST
api.add_resource(UserResource, '/users/<int:user_id>')  # GET, PUT, DELETE

# TODO сделано
api.add_resource(TokenResource, '/auth/token')  # GET

# TODO сделано
api.add_resource(NotesListResource, '/notes')  # GET, POST
api.add_resource(NoteResource, '/notes/<int:note_id>')  # GET, PUT, DELETE

# TODO сделано
api.add_resource(NoteTagsResource, '/notes/<int:note_id>/tags')  # PUT # DELETE

# TODO сделано
api.add_resource(TagsListResource, '/tags')  # GET, POST
api.add_resource(TagsResource, '/tags/<int:tag_id>')  # GET, PUT, DELETE

# TODO частично сделано
api.add_resource(NoteFilterResource, '/notes/filter')  # GET notes by user / user + tag

# TODO сделано
api.add_resource(NotesFilterByTagResource, '/notes/filter/tag')  # GET All Public Notes or notes by Tags (need auth)

# api.add_resource(NoteTagResource, '/notes/filter/1/tag')
# docs.register(NoteTagResource)
#
# api.add_resource(NoteTexResource, '/notes/text')
# docs.register(NoteTexResource)

docs.register(UserResource)
docs.register(UsersListResource)

docs.register(NoteResource)
docs.register(NotesListResource)

docs.register(NoteTagsResource)

docs.register(TagsResource)
docs.register(TagsListResource)

docs.register(NoteFilterResource)
docs.register(NotesFilterByTagResource)

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
