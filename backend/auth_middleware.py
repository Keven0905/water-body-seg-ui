from flask import request, g
import jwt
from config import Config


def init_auth_middleware(app):
    @app.before_request
    def load_user():
        g.current_user = None
        token = request.cookies.get('token')
        if not token:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
        if not token:
            return
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            g.current_user = {'username': payload['sub'], 'role': payload['role']}
        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass
