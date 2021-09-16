from api import Resource, g, auth
from api import api


@api.resource('/auth/token')
class TokenResource(Resource):
    @auth.login_required
    def get(self):
        token = g.user.generate_auth_token()
        return {'token': token.decode('ascii')}
