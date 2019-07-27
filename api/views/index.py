from flask import jsonify, request, Response
from api import app
from api.utils.db import mongodata
from api.utils.db import Users
import sqlite3 as sql
import jwt
from datetime import datetime
import json
md = mongodata()
def auth_token_check(token):
    decoded = jwt.decode(token, 'iamnotme123', algorithms=['HS256'])
    time_then = datetime.strptime(decoded['date_time'],'%d/%m/%y %H:%M:%S')
    time_now = datetime.now()
    time_diff = time_now - time_then 
    hours = divmod(time_diff.total_seconds(), 3600)[0]
    if hours < 1:
        return True
    else:
        return False

def encode(password):
    date_time = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    encoded = jwt.encode({'password':password,'date_time':str(date_time)}, "iamnotme123", algorithm='HS256')
    return encoded

def jsonify_status_code(**kw):
    response = jsonify(**kw)
    response.status_code = kw['code']
    return response

@app.route('/auth', methods=['POST'],strict_slashes = False)
def auth():
    auth = request.authorization
    users = Users()
    if users.check_user(auth['username'],auth['password']):
        return jsonify_status_code(code=200,data=encode(auth['password']))
    else:
        return jsonify_status_code(code=200,data= "invalid Username")

@app.route('/test', methods=['POST'],strict_slashes = False)
def test():
    data = request.json 
    if auth_token_check(data['jwt']):
        return jsonify_status_code(code=200,data="Valid authorization")
    else:
        return jsonify_status_code(code=200,data= "invalid authorization")

@app.route('/device_list', methods=['POST'],strict_slashes = False)
def device_list():
    data = request.json 
    if auth_token_check(data['jwt']):
        list_devices = md.get_devices()
        return jsonify_status_code(code=200,devices=list_devices)
    else:
        return jsonify_status_code(code=200,data= "invalid authorization")

@app.route('/devices', methods=['POST'],strict_slashes = False)
def devices():
    data = request.json 
    if auth_token_check(data['jwt']):
        if data.get('id'):
            if data.get('page'):
                list_status_for_device = md.get_status_for_device_page(data['id'],data['page'])
                return jsonify_status_code(code=200,devices=list_status_for_device)
            else:            
                list_status_for_device = md.get_status_for_device(data['id'])
                return jsonify_status_code(code=200,devices=list_status_for_device)
        else:            
            return jsonify_status_code(code=200,message= "invalid input")
    else:
        return jsonify_status_code(code=200,message= "invalid authorization")

@app.route('/halts', methods=['POST'],strict_slashes = False)
def halts():
    data = request.json 
    if auth_token_check(data['jwt']):
        return jsonify_status_code(code=200,data=md.find_halts())
    else:
        return jsonify_status_code(code=200,message= "invalid authorization")


