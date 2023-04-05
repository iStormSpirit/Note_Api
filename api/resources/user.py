import logging

from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from flask_babel import gettext
from webargs import fields

from api import abort, api, auth, g
from api.models.file import FileModel
from api.models.user import UserModel
from api.schemas.user import (UserCreateSchema, UserEditSchema,
                              UserPhotoSchema, UserSchema)


@doc(tags=['Users'])
@api.resource('/users/<int:user_id>')
class UserResource(MethodResource):
    @doc(summary="Get User by id", description='Get user by id')
    @marshal_with(UserSchema, code=200)
    def get(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=gettext("User with id %(user_id)s not found", user_id=user_id))
        return user, 200  # user_schema.dump(user) благодаря @marshal_with(UserSchema) теперь не нужен

    @auth.login_required
    @doc(summary="Edit User by id", description='Edit user by id', security=[{"basicAuth": []}])
    @marshal_with(UserSchema, code=200)
    @use_kwargs(UserEditSchema, location='json')
    def put(self, user_id, **kwargs):
        author = g.user
        user = UserModel.query.get(user_id)
        if user != author:
            abort(403, error=f"Forbidden")
        if not user:
            abort(404, error=gettext("User with id %(user_id)s not found", user_id=user_id))
        if kwargs.get("username") is not None:
            user.username = kwargs["username"]
        user.save()
        return user, 200

    @auth.login_required(role="admin")
    @doc(summary="Delete User by id", description='Delete user by id.')
    @doc(responses={401: {"description": "Not authorization"}})
    @doc(responses={404: {"description": "Not found"}})
    @marshal_with(UserSchema, code=200)
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if user:
            user.delete()
            return user, 200
        abort(404, error=gettext("User with id %(user_id)s not found", user_id=user_id))


@doc(tags=['Users'])
@api.resource('/users')
class UsersListResource(MethodResource):
    @doc(summary="Get Users", description='Get users')
    @marshal_with(UserSchema(many=True), code=200)
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @doc(summary="Create Users", description='Create users')
    @use_kwargs(UserCreateSchema, location='json')
    @marshal_with(UserSchema, code=201)
    def post(self, **kwargs):
        if kwargs.get("photo_id"):
            photo_id = kwargs["photo_id"]
            del kwargs["photo_id"]
            photo = FileModel.query.get(photo_id)
            kwargs["photo"] = photo
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            abort(400, error=f"User with username:{user.username} already exist")
        logging.info("User create!!!")
        return user, 201
    # def post(self, **kwargs):
    #     user = UserModel(**kwargs)
    #     user.save()
    #     if not user.id:
    #         abort(400, error=f"User with username:{user.username} already exist")
    #     logging.info("User create!!!")
    #     return user, 201


@doc(tags=['Users extra options'])
@api.resource('/users/any')
class UserFindOrResource(MethodResource):
    @doc(summary="Find any of user by name", description='Find any of user by name')
    @use_kwargs({"username": fields.Str(), "username2": fields.Str()}, location='query')
    @marshal_with(UserSchema(many=True), code=200)
    def get(self, **kwargs):
        if "username" and "username2" in kwargs:
            users = UserModel.query.filter(
                (UserModel.username == kwargs["username"]) |
                (UserModel.username == kwargs["username2"]))
            return users, 200
        if "username" in kwargs:
            users = UserModel.query.filter(UserModel.username == kwargs["username"])
            return users, 200
        abort(400, error=gettext("Need key to search"))


@doc(tags=['Users extra options'])
@api.resource('/users/like')
class UserFindLikeResource(MethodResource):
    @doc(summary="Find users like ", description='Find users like')
    @use_kwargs({"username": fields.String(load_default="")}, location='query')
    @marshal_with(UserSchema(many=True), code=200)
    def get(self, username):
        if username:
            users = UserModel.query.filter(UserModel.username.like(f"%{username}%"))
            return users, 200
        abort(400, error=gettext("Need key to search"))


@doc(tags=['Users extra options'])
@api.resource('/users/<int:user_id>/photo')
class UserAddPhotoResource(MethodResource):
    @auth.login_required
    @doc(summary="Add photo to user", description='Add photo to user', security=[{"basicAuth": []}])
    @marshal_with(UserSchema, code=200)
    @use_kwargs(UserPhotoSchema, location='json')
    def put(self, user_id, photo_id):
        author = g.user
        user = UserModel.query.get(user_id)
        if user != author:
            abort(403, error=f"Forbidden")
        if photo_id is not None:
            user.photo_id = photo_id
        user.save()
        return user, 200
