from flask import Blueprint, request, jsonify, make_response
import jwt
import datetime
from config import Config
from services.auth import verify_user, register_user

bp = Blueprint('auth', __name__)


def _create_token(username: str, role: str) -> str:
    payload = {
        'sub': username,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': '请输入用户名和密码'}), 400

    user = verify_user(data['username'], data['password'])
    if not user:
        return jsonify({'success': False, 'error': '用户名或密码错误'}), 401

    token = _create_token(user['username'], user['role'])
    resp = make_response(jsonify({'success': True, 'user': user}))
    resp.set_cookie('token', token, httponly=True, samesite='Lax', max_age=86400)
    return resp


@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': '请输入用户名和密码'}), 400

    if len(data['username']) < 2 or len(data['password']) < 4:
        return jsonify({'success': False, 'error': '用户名至少2字符，密码至少4字符'}), 400

    user = register_user(data['username'], data['password'])
    if not user:
        return jsonify({'success': False, 'error': '用户名已存在'}), 409

    token = _create_token(user['username'], user['role'])
    resp = make_response(jsonify({'success': True, 'user': user}))
    resp.set_cookie('token', token, httponly=True, samesite='Lax', max_age=86400)
    return resp


@bp.route('/api/me', methods=['GET'])
def me():
    from flask import g
    if not hasattr(g, 'current_user') or g.current_user is None:
        return jsonify({'error': '未登录'}), 401
    return jsonify(g.current_user)


@bp.route('/api/logout', methods=['POST'])
def logout():
    resp = make_response(jsonify({'success': True}))
    resp.delete_cookie('token')
    return resp
