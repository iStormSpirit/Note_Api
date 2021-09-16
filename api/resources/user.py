from api import abort, auth
from api.models.user import UserModel
from api.schemas.user import UserSchema, UserRequestSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields
import logging


@doc(tags=['Users'])
class UserResource(MethodResource):
    @doc(summary="Get User by id", description='Get user by id')
    @marshal_with(UserSchema)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200  # user_schema.dump(user) благодаря @marshal_with(UserSchema) теперь не нужен

    @auth.login_required(role="admin")
    @doc(summary="Edit User by id", description='Edit user by id', security=[{"basicAuth": []}])
    @marshal_with(UserSchema)
    @use_kwargs({"username": fields.Str()})
    def put(self, user_id, **kwargs):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.username = kwargs["username"]
        user.save()
        return user, 200

    @auth.login_required(role="admin")
    @doc(summary="Delete User by id", description='Delete user by id.')
    @doc(responses={401: {"description": "Not authorization"}})
    @doc(responses={404: {"description": "Not found"}})
    @marshal_with(UserSchema)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            user.remove()
            return user, 200
        abort(404, error=f"Not Found user {user_id}")


@doc(tags=['Users'])
class UsersListResource(MethodResource):
    @doc(summary="Get Users", description='Get users')
    @marshal_with(UserSchema(many=True))
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @doc(summary="Create Users", description='Create users')
    @use_kwargs(UserRequestSchema, location='json')
    @marshal_with(UserSchema)
    def post(self, **kwargs):
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} already exist")
        logging.info("User create!!!")
        return user, 201


# FIXME добавить найти только user2
@doc(tags=['Users'])
class UserFindOrResource(MethodResource):
    @doc(summary="Find find any of user by name",
         description='Find find any of user by name')
    @use_kwargs({"username": fields.Str(), "username2": fields.Str()}, location='query')
    @marshal_with(UserSchema(many=True))
    def get(self, **kwargs):
        if "username" and "username2" in kwargs:
            users = UserModel.query.filter(
                (UserModel.username == kwargs["username"]) |
                (UserModel.username == kwargs["username2"]))
            return users, 200
        if "username" in kwargs:
            users = UserModel.query.filter(UserModel.username == kwargs["username"])
            return users, 200
        abort(404, error="Not key for search")


@doc(tags=['Users'])
class UserFindLikeResource(MethodResource):
    @doc(summary="Find find any of user by name",
         description='Find find any of user by name')
    @use_kwargs({"username": fields.String(load_default="")}, location='query')
    @marshal_with(UserSchema(many=True))
    def get(self, username):
        if username:
            users = UserModel.query.filter(UserModel.username.like(f"%{username}%"))
            return users, 200
        abort(404, error=f"Need key to search")
