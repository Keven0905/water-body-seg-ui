import os
import json
import hashlib
from config import Config

USERS_FILE = os.path.join(Config.BASE_DIR, 'users.json')

DEFAULT_USERS = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin'},
    {'username': 'user', 'password': 'user123', 'role': 'user'},
]


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def _load_users() -> list:
    if not os.path.exists(USERS_FILE):
        _init_default_users()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)['users']


def _save_users(users: list):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'users': users}, f, ensure_ascii=False, indent=2)


def _init_default_users():
    users = []
    for u in DEFAULT_USERS:
        users.append({
            'username': u['username'],
            'password_hash': _hash_password(u['password']),
            'role': u['role'],
        })
    _save_users(users)


def verify_user(username: str, password: str) -> dict | None:
    users = _load_users()
    pw_hash = _hash_password(password)
    for u in users:
        if u['username'] == username and u['password_hash'] == pw_hash:
            return {'username': u['username'], 'role': u['role']}
    return None


def register_user(username: str, password: str) -> dict | None:
    users = _load_users()
    for u in users:
        if u['username'] == username:
            return None
    new_user = {
        'username': username,
        'password_hash': _hash_password(password),
        'role': 'user',
    }
    users.append(new_user)
    _save_users(users)
    return {'username': username, 'role': 'user'}


def get_user_by_username(username: str) -> dict | None:
    users = _load_users()
    for u in users:
        if u['username'] == username:
            return {'username': u['username'], 'role': u['role']}
    return None
