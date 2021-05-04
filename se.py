# Project 2
# Khalen Stensby
# CPSC 449 Friday

import json
import gensim
from gensim.parsing.preprocessing import remove_stopwords
import sys
import textwrap
import logging.config
import redis
import string
import requests
import bottle
from bottle import get, post, error, delete, abort, request, response, HTTPResponse

app = bottle.default_app()

r = redis.Redis()

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

# Routes
# /index/ id=1 etc...
@get('/index/')
def index():
	index_id = request.json

	if not index_id:
		abort(400)
	
	posted_fields = index_id.keys()
	required_fields = {'id'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')

	idx = index_id.get('id')
	timelines_req = requests.get('http://localhost:5100/timelines/id/'+idx)
	data = timelines_req.json()['data'][0]['text']
	lower = data.lower()
	for c in string.punctuation:
		lower = lower.replace(c, "")
	remove_sw = remove_stopwords(lower)
	tokens = remove_sw.split()

	for t in tokens:
		r.sadd(t, idx)

	response.status = 200

	return timelines_req.json()

# /search/ kw=word
@get('/search/')
def search():
	kw = request.json

	if not kw:
		abort(400)

	posted_fields = kw.keys()
	required_fields = {'kw'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')

	kw = kw.get('kw')
	kw = kw.lower()
	l = []

	if r.exists(kw) == 1:
		l = r.smembers(kw)

	j = []
	for member in l:
		j.append(int(member.decode('UTF-8')))

	json_return = json.dumps(j)

	response.status = 200

	return {'index': json_return}


# Send as /any/ kw=kw1+kw2+kw3... etc
@get('/any/')
def any():
	kw = request.json

	if not kw:
		abort(400)

	posted_fields = kw.keys()
	required_fields = {'kw'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')
	
	kw = kw.get('kw')
	kw = kw.lower()
	query = kw.split('+')
	l = []

	for w in query:
		if r.exists(w) == 1:
			l.append(r.smembers(w))

	j = []
	for s in l:
		for member in s:
			if int(member.decode('UTF-8')) not in j:
				j.append(int(member.decode('UTF-8')))

	json_return = json.dumps(j)

	response.status = 200

	return {'index': json_return}

# Send as /all/ kw=kw1+kw2+kw3... etc
@get('/all/')
def all():
	kw = request.json

	if not kw:
		abort(400)

	posted_fields = kw.keys()
	required_fields = {'kw'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')
	
	kw = kw.get('kw')
	kw = kw.lower()
	query = kw.split('+')
	l = []

	dead_query = False

	for w in query:
		if r.exists(w) == 1:
			l.append(r.smembers(w))
		else:
			dead_query = True

	if not dead_query:
		temp = 0
		smallest = sys.maxsize
		i = 0
		# find smallest set in our list
		for s in l:
			if len(s) < smallest:
				smallest = len(s)
				temp = i
			i += 1

		smallest_set = l[temp]
		j = []

		for x in smallest_set:
			in_all = True
			for s in l:
				if x not in s:
					in_all = False
			if in_all == True:
				j.append(int(x.decode('UTF-8')))	

		json_return = json.dumps(j)

		response.status = 200

		return {'index': json_return}

	else:
		return {'index': ['empty']}

# Send as /exclude/ inc=kw1+kw2+kw3 exc=ew1+ew2+ew3... etc
@get('/exclude/')
def exclude():
	req = request.json

	if not req:
		abort(400)

	posted_fields = req.keys()
	required_fields = {'inc', 'exc'}

	if not required_fields <= posted_fields:
		abort(400, f'Missing fields: {required_fields - posted_fields}')
	
	inc = req.get('inc')
	exc = req.get('exc')
	inc = inc.lower()
	exc = exc.lower()
	query = inc.split('+')
	anti_query = exc.split('+')
	inc_set_list = []
	exc_set_list = []

	for inc_word in query:
		if r.exists(inc_word) == 1:
			inc_set_list.append(r.smembers(inc_word))

	for exc_word in anti_query:
		if r.exists(exc_word) == 1:
			exc_set_list.append(r.smembers(exc_word))

	j_inc = []
	for s in inc_set_list:
		for member in s:
			if int(member.decode('UTF-8')) not in j_inc:
				j_inc.append(int(member.decode('UTF-8')))

	j_exc = []
	for s in exc_set_list:
		for member in s:
			if int(member.decode('UTF-8')) not in j_exc:
				j_exc.append(int(member.decode('UTF-8')))

	for m in j_exc:
		if m in j_inc:
			j_inc.remove(m)
	
	json_return = json.dumps(j_inc)

	response.status = 200

	return {'index': json_return}
