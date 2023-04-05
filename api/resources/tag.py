from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_babel import gettext
from webargs import fields

from api import abort, api, auth
from api.models.tag import TagModel
from api.schemas.tag import TagSchema


@doc(tags=['Tags'])
@api.resource('/tags/<int:tag_id>')
class TagsResource(MethodResource):
    @marshal_with(TagSchema, code=200)
    @doc(summary="Get tag by tag id", description='Get tags by tag id')
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=gettext("Tag with id %(tag_id)s not found", tag_id=tag_id))
        return tag, 200

    @auth.login_required(role="admin")
    @doc(summary="Edit tag by tag id", description='Edit tags by id', security=[{"basicAuth": []}])
    @marshal_with(TagSchema, code=200)
    @use_kwargs({"name": fields.Str()})
    def put(self, tag_id, **kwargs):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=gettext("User with id %(tag_id)s not found", tag_id=tag_id))
        tag.name = kwargs["name"]
        tag.save()
        return tag, 200

    @auth.login_required(role="admin")
    @doc(summary="Delete tag by tag id", description='Delete tag by id', security=[{"basicAuth": []}])
    @marshal_with(TagSchema, code=200)
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if tag:
            tag.delete()
            return tag, 200
        abort(404, error=gettext("Tag with id %(tag_id)s not found", tag_id=tag_id))


@doc(tags=['Tags'])
@api.resource('/tags')
class TagsListResource(MethodResource):
    @doc(summary="Get all tags", description='Get all tags')
    @marshal_with(TagSchema(many=True), code=200)
    def get(self):
        tags = TagModel.query.all()
        if not tags:
            abort(404, error=gettext("Tags not found"))
        return tags, 200

    @doc(summary="Create tags", description='Create tags')
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema, code=201)
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        return tag, 201
