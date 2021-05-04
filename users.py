# Project 2
# Khalen Stensby
# CPSC 449 Friday

import sys
import textwrap
import logging.config
import sqlite3

import bottle
from bottle import get, post, error, delete, abort, request, response, HTTPResponse
from bottle.ext import sqlite

app = bottle.default_app()
app.config.load_config('./etc/users.ini')

plugin = sqlite.Plugin(app.config['sqlite.dbfile'])
app.install(plugin)

#logging.config.fileConfig(app.config['logging.config'])

# Return errors in JSON

def json_error_handler(res):
    if res.content_type == 'application/json':
        return res.body
    res.content_type = 'application/json'
    if res.body == 'Unknown Error.':
        res.body = bottle.HTTP_Codes[res.status_code]
        return bottle.json_dumps({'error': res.body})

app.default_error_handler = json_error_handler

# Disable Bottle warnings

if not sys.warnoptions:
    import warnings
    for warning in [DeprecationWarning, ResourceWarning]:
        warnings.simplefilter('ignore', warning)

# Simple DB access
def query(db, sql, args=(), one=False):
    cur = db.execute(sql, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row))
          for row in cur.fetchall()]
    cur.close()

    return (rv[0] if rv else None) if one else rv

def execute(db, sql, args=()):
    cur = db.execute(sql, args)
    id = cur.lastrowid
    cur.close()

    return id

# Routes

@get('/users/')
def users(db):
    all_users = query(db, 'SELECT * FROM users;')

    response.status = 200
    response.set_header('Location', f"/users/")
    return {'users': all_users}

@get('/follows/')
def follows(db):
    all_follows = query(db, 'SELECT * FROM follows;')

    return {'follows': all_follows}

@post('/users/create_user/')
def create_user(db):
    user = request.json

    if not user:
        abort(400)

    posted_fields = user.keys()
    required_fields = {'username', 'email', 'password'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        user['id'] = execute(db, '''
            INSERT INTO users(username, email, password)
            VALUES(:username, :email, :password)
            ''', user)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    response.set_header('Location', f"/users/{user['id']}")
    return user

@get('/users/check_password/')
def check_password(db):
    user = request.json

    posted_fields = user.keys()
    required_fields = {'username', 'password'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    json = query(db, 'SELECT password FROM users WHERE username = ?', [user['username']], one=True)

    if user['password'] == json['password']:
        response.status = 302
        return user
    response.status = 404
    return user

@delete('/follows/remove_follower/')
def remove_follower(db):
    removes = request.json

    if not removes:
        abort(400)

    posted_fields = removes.keys()
    required_fields = {'username', 'follows'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    json = query(db, 'SELECT id FROM follows WHERE username = ? AND follows = ?', [removes['username'], removes['follows']])

    delete = execute(db,'DELETE FROM follows WHERE id = ?', str(json[0]['id']))

    response.status = 202
    return removes


@post('/follows/add_follower/')
def add_follower(db):
    follows = request.json

    if not follows:
        abort(400)

    posted_fields = follows.keys()
    required_fields = {'username', 'follows'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    try:
        follows['id'] = execute(db, '''
            INSERT INTO follows(username, follows)
            VALUES(:username, :follows)
            ''', follows)
    except sqlite3.IntegrityError as e:
        abort(409, str(e))

    response.status = 201
    response.set_header('Location', f"/follows/{follows['id']}")
    return follows

