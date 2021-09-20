from api import app, docs
from api.resources.note import NoteResource, NotesListResource, NoteTagsResource, \
    NoteTexResource, NoteRestoreResource, NoteFilterTagsResource
from api.resources.user import UserResource, UsersListResource, UserFindOrResource, \
    UserFindLikeResource, UserAddPhotoResource
from api.resources.tag import TagsResource, TagsListResource
from config import Config
from api import Message, mail
from api.resources.file import UploadPictureResource
from flask import send_from_directory, render_template


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


docs.register(UserResource)
docs.register(UsersListResource)
docs.register(UserAddPhotoResource)
docs.register(UserFindOrResource)
docs.register(UserFindLikeResource)
docs.register(NoteResource)
docs.register(NotesListResource)
docs.register(NoteRestoreResource)
docs.register(NoteTagsResource)
docs.register(NoteTexResource)
docs.register(NoteFilterTagsResource)
docs.register(TagsResource)
docs.register(TagsListResource)
docs.register(UploadPictureResource)

msg = Message('test subject', sender=Config.ADMINS[0], recipients=Config.ADMINS)
msg.body = 'text body'
msg.html = '<b>HTML</b> body'

if __name__ == '__main__':
    # with app.app_context():
    #     mail.send(msg)
    app.run(debug=Config.DEBUG, port=Config.PORT)
