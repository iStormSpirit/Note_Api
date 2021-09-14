from api import api, app, docs
from api.resources.note import NoteResource, NotesListResource, NoteTagsResource, NotesFilterByTagResource, \
    NoteFilterResource, NoteTexResource, NoteRestoreResource  # , NotesListTagResource
from api.resources.user import UserResource, UsersListResource, UserFindOrResource
from api.resources.auth import TokenResource
from api.resources.tag import TagsResource, TagsListResource

api.add_resource(UsersListResource, '/users')  # GET, POST
api.add_resource(UserResource, '/users/<int:user_id>')  # GET, PUT, DELETE
api.add_resource(UserFindOrResource, '/users/or')  # GET Find user1 or user2

api.add_resource(TokenResource, '/auth/token')  # GET

api.add_resource(NotesListResource, '/notes')  # GET, POST
api.add_resource(NoteResource, '/notes/<int:note_id>')  # GET, PUT, DELETE (delet = archive)
api.add_resource(NoteRestoreResource, '/notes/<int:note_id>/restore')  # PUT (back notes from archive)

api.add_resource(NoteTagsResource, '/notes/<int:note_id>/tags')  # PUT # DELETE

api.add_resource(TagsListResource, '/tags')  # GET, POST
api.add_resource(TagsResource, '/tags/<int:tag_id>')  # GET, PUT, DELETE

# FIXME частично сделано, добавить фильтрацию только по тегу + публичные/приватные/все
api.add_resource(NoteFilterResource, '/notes/filter')  # GET notes by user / user + tag

api.add_resource(NotesFilterByTagResource, '/notes/filter/tag')  # GET All Public Notes or notes by Tags (need auth)
api.add_resource(NoteTexResource, '/notes/text')  # GET Find all notes with text

# api.add_resource(NotesListTagResource, '/notes/list/tags')
# docs.register(NotesListTagResource)


docs.register(UserResource)
docs.register(UsersListResource)
docs.register(UserFindOrResource)

docs.register(NoteResource)
docs.register(NotesListResource)
docs.register(NoteRestoreResource)

docs.register(NoteTagsResource)

docs.register(TagsResource)
docs.register(TagsListResource)

docs.register(NoteFilterResource)
docs.register(NotesFilterByTagResource)

docs.register(NoteTexResource)

from config import Config
from api import Message, mail

msg = Message('test subject', sender=Config.ADMINS[0], recipients=Config.ADMINS)
msg.body = 'text body'
msg.html = '<b>HTML</b> body'

if __name__ == '__main__':
    # with app.app_context():
    #     mail.send(msg)
    app.run(debug=Config.DEBUG, port=Config.PORT)
