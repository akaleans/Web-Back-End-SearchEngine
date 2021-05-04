# Project 2
# Khalen Stensby
# CPSC 449 Friday

import sys
import textwrap
import logging.config
import sqlite3
import requests
import bottle
from bottle import get, post, error, delete, abort, request, response, HTTPResponse
from bottle.ext import sqlite

app = bottle.default_app()
app.config.load_config('./etc/timelines.ini')

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

@get('/timelines/')
def timelines(db):
    all_timelines = query(db, 'SELECT * FROM timelines;')
    return {'timelines': all_timelines}

@get('/timelines/id/<idx>')
def timeline_id(db, idx):
#	idx = request.json

#	if not idx:
#		abort(400)

#	posted_fields = idx.keys()
#	required_fields = {'id'}

#	if not required_fields <= posted_fields:
#		abort(400, f'Missing fields: {required_fields - posted_fields}')

	json = query(db, 'SELECT text FROM timelines WHERE id = ?', idx)

	return {'data': json}

@get('/timelines/user/')
def user_timeline(db):
	user = request.json

	if not user:
		abort(400)

	posted_fields = user.keys()
	required_fields = {'username'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')

	json = query(db, 'SELECT * FROM timelines WHERE username = ?', [user['username']], one=False)

	return {'timelines': json}

@get('/timelines/home/')
def home_timeline(db):
	user = request.json

	parse = user['follows']
	params = parse.split('+')

	json = []
	for x in params:
		json.append((query(db, 'SELECT * FROM timelines WHERE username = ?', [x], one=False)))

	return {'timelines': json}

@post('/timelines/post_tweet/')
def post_tweet(db):
	tweet = request.json

	if not tweet:
		abort(400)

	posted_fields = tweet.keys()
	required_fields = {'username', 'text'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')

	try:
		tweet['id'] = execute(db, '''
		INSERT INTO timelines(username, text, time)
		VALUES(:username, :text, CURRENT_TIMESTAMP);
		''', tweet)
	
	except sqlite3.IntegrityError as e:
		abort(409, str(e))

	response.status = 201
	response.set_header('Location', f"/timelines/{tweet['id']}")
	return tweet
