# Project 5
# Khalen Stensby
# CPSC 449 Friday

import sys
import textwrap
import logging.config
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
from datetime import datetime
from pprint import pprint

import bottle
from bottle import get, post, error, delete, abort, request, response, HTTPResponse

app = bottle.default_app()
#app.config.load_config('./etc/users.ini')

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

# Quick Replies
quick_replies = ['OK', 'Yes', 'No', 'On my way!']

# Routes
@get('/dms/all/')
def all(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    
    table = dynamodb.Table('dms_table4')
    scan = table.scan()
    return scan

@get('/dms/user_dms/')
def user_dms(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    
    table = dynamodb.Table('dms_table4')
    
    req = request.json
    if not req:
        abort(400)

    db_resp = table.scan(FilterExpression=Attr('from').eq(req['username']))

    response.status = 200
    response.set_header('Location', f"/dms/user_dms/")
    return db_resp

@get('/dms/replies/')
def follows(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
    
    table = dynamodb.Table('dms_table4')
    
    req = request.json
    if not req:
        abort(400)

    db_resp = table.scan(FilterExpression=Attr('reply_to').eq(req['msg_id']))

    response.status = 200
    response.set_header('Location', f"/dms/replies/")
    return db_resp

@post('/dms/send_dm/')
def send_dm(dynamodb=None):
    req = request.json

    if not req:
        abort(400)

    posted_fields = req.keys()
    required_fields = {'to', 'from', 'text'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('dms_table4')

    time = str(datetime.now())
    resp = table.scan()
    count = resp['ScannedCount']
    count += 1

    if required_fields == posted_fields:
        db_resp = table.put_item(Item={
            'msg_id': str(count),
            'text': req['text'],
            'time': time,
            'from': req['from'],
            'to': req['to'],
            'reply': 'no',
            'reply_to': '0',
			'qrf': 'no'
            })
    else:
        db_resp = table.put_item(Item={
            'msg_id': str(count),
            'text': req['text'],
            'time': time,
            'from': req['from'],
            'to': req['to'],
            'reply': 'no',
            'reply_to': '0',
			'qrf': req['qrf']
            })

    response.status = 201
    response.set_header('Location', f"/dms/send_dm/")
    return db_resp

@post('/dms/reply_to/')
def send_dm(dynamodb=None):
    req = request.json

    if not req:
        abort(400)

    posted_fields = req.keys()
    required_fields = {'msg_id', 'text'}

    if not required_fields <= posted_fields:
        abort(400, f'Missing fields: {required_fields - posted_fields}')

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")

    table = dynamodb.Table('dms_table4')
    scan_resp = table.scan()
    count = scan_resp['ScannedCount']
    count += 1
    time = str(datetime.now())
    resp = table.scan(FilterExpression=Attr('msg_id').eq(req['msg_id']))
    for i in resp['Items']:
        to_user = i['from']
        from_user = i['to']
        qrf = i['qrf']

    if (qrf == 'yes') and (req['text'] == '0' or req['text'] == '1' or req['text'] == '2' or req['text'] == '3'):
        qr = int(req['text'])
        db_resp = table.put_item(Item={
            'msg_id': str(count),
            'text': quick_replies[qr],
            'time': time,
            'from': from_user,
            'to': to_user,
            'reply': 'yes',
            'reply_to': req['msg_id'],
            'qrf': 'no'
            })
    else:
        db_resp = table.put_item(Item={
            'msg_id': str(count),
            'text': req['text'],
            'time': time,
            'from': from_user,
            'to': to_user,
            'reply': 'yes',
            'reply_to': req['msg_id'],
            'qrf': 'no'
            })
        

    response.status = 201
    response.set_header('Location', f"/dms/reply_to/")
    return db_resp

