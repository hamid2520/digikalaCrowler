from flask import request

from db.models import User, Token
from db.connection import db_session
import datetime
import json
from hashlib import sha256

PASSWORD_KEY = 'DHUIHF27^&*@!HD*(!)@#UWIJDPOACQW)(@HF#*QWU_D(JQSPEIUFHQE(*!@'
TOKEN_KEY = 'duuSY&D#@Y&E*Hhasudy1c7hy&YH*&@ECQE'


def check_username(username):
    return 3 < len(username) < 128 and User.query.filter(User.username == username).first() is None


def register():
    if 'first_name' in request.form and 'last_name' in request.form and 'password' in request.form and \
            'username' in request.form and 'email' in request.form and 'phone' in request.form:
        if not check_username(request.form['username']):
            return json.dumps({
                'success': False,
                'error': 'invalid username'
            })
        user = User()
        user.username = request.form['username']
        user.email = request.form['email']
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.phone = request.form['phone']
        user.password = sha256(request.form['password'] + PASSWORD_KEY).hexdigest()
        db_session.add(user)
        db_session.commit()
        token = Token()
        token.user_id = user.id
        token.key = sha256(user.username + str(user.id) + str(datetime.datetime.utcnow()) + TOKEN_KEY).hexdigest()
        db_session.add(token)
        db_session.commit()
        return json.dumps({
            'success': True,
            'user': user.serialize(),
            'token': token.key
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })


def login():
    if 'password' in request.form and (
            'email' in request.form or 'username' in request.form or 'phone' in request.form):
        user = None
        if 'username' in request.form:
            user = User.query.filter(User.username == request.form['username']).first()
        elif 'email' in request.form:
            user = User.query.filter(User.email == request.form['email']).first()
        elif 'phone' in request.form:
            user = User.query.filter(User.phone == request.form['phone']).first()
        if user is not None and user.password == sha256(request.form['password'] + PASSWORD_KEY).hexdigest():
            token = Token()
            token.key = sha256(user.username + str(user.id) + str(datetime.datetime.utcnow()) + TOKEN_KEY).hexdigest()
            token.user_id = user.id
            user.last_seen = datetime.datetime.utcnow()
            db_session.add(token)
            db_session.add(user)
            db_session.commit()
            return json.dumps({
                'success': True,
                'user': user.serialize(),
                'token': token.key
            })
        return json.dumps({
            'success': False,
            'error': 'user not found'
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })


def check():
    if 'user_id' in request.form and 'token' in request.headers:
        token = Token.query.filter(Token.key == request.headers['token'], Token.user_id == request.form['user_id']) \
            .first()
        if token is not None:
            token.last_activity = datetime.datetime.utcnow()
            token.user.last_seen = datetime.datetime.utcnow()
            db_session.add(token)
            db_session.commit()
            return json.dumps({
                'success': True,
                'user': token.user.serialize(),
                'token': token.key
            })
        return json.dumps({
            'success': False,
            'error': 'invalid token'
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })
