from api import Resource, abort, reqparse, auth, db
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema, UserSchema, UserRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields


@doc(tags=['Users'])
class UserResource(MethodResource):
    @doc(description='Get user by id')
    @marshal_with(UserSchema)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200  # user_schema.dump(user) благодаря @marshal_with(UserSchema) теперь не нужен

    @auth.login_required(role="admin")
    @doc(description='Edit user by id')
    @marshal_with(UserSchema)
    @use_kwargs({"username": fields.Str()})
    @doc(security=[{"basicAuth": []}])
    def put(self, user_id, **kwargs):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.username = kwargs["username"]
        user.save()
        return user, 200

    @auth.login_required(role="admin")
    @doc(description='Delete user by id.')
    @marshal_with(UserSchema)
    @doc(security=[{"basicAuth": []}])
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            user.remove()
            return user, 200
        return "Not found", 404


@doc(tags=['Users'])
class UsersListResource(MethodResource):
    @doc(description='Get users')
    @marshal_with(UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @use_kwargs(UserRequestSchema, location='json')
    @marshal_with(UserSchema)
    def post(self, **kwargs):
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} already exist")
        return user, 201
