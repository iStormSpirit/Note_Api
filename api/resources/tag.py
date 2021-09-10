from api import auth, abort, g, Resource, reqparse
from api.models.tag import TagModel
from api.schemas.tag import TagSchema, TagRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Tags'])
class TagsResource(MethodResource):
    @marshal_with(TagSchema)
    @doc(description='Get tags by tag id', summary="Get Tag")
    def get(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"Tag with id={tag_id} not found")
        return tag, 200

    @auth.login_required(role="admin")
    @doc(description='Edit note by id')
    @marshal_with(TagSchema)
    @use_kwargs({"name": fields.Str()})
    @doc(security=[{"basicAuth": []}])
    def put(self, tag_id, **kwargs):
        tag = TagModel.query.get(tag_id)
        if not tag:
            abort(404, error=f"User with id={tag_id} not found")
        tag.name = kwargs["name"]
        tag.save()
        return tag, 200

    @auth.login_required(role="admin")
    @doc(description='Delete tag by id')
    @marshal_with(TagSchema)
    @doc(security=[{"basicAuth": []}])
    def delete(self, tag_id):
        tag = TagModel.query.get(tag_id)
        if tag:
            tag.delete()
            return tag, 200
        abort(404, error=f"Tag with id={tag_id} not found")


@doc(tags=['Tags'])
class TagsListResource(MethodResource):
    @doc(description='Get tags')
    @marshal_with(TagSchema(many=True))
    def get(self):
        tags = TagModel.query.all()
        if not tags:
            abort(404, error=f"Tags not found")
        return tags, 200

    @doc(description='Create tags')
    @use_kwargs({"name": fields.Str()})
    @marshal_with(TagSchema)
    def post(self, **kwargs):
        tag = TagModel(**kwargs)
        tag.save()
        return tag, 201
