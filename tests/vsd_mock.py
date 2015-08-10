import sys
from flask import Flask, request, make_response
import json
from time import time as epoch

#from common import exception


app = Flask(__name__)

database = {}

database.update({
    'enterprises': [
        {'ID': '1234-5678-1234567890',
         'name': 'nulab-1',
         'description': 'None',
         'parentType': 'null',
         'enterpriseProfileID': '1234-5678-1234567890'},
        {'ID': '1111-2222-1122334455',
         'name': 'nulab-2',
         'description': 'None',
         'parentType': 'null',
         'enterpriseProfileID': '1234-5678-1234567890'}]
})

database.update({
    'messages': [
        {'name': 'already exists',
         'message': {
             'errors': [{
                 'property': 'name',
                 'descriptions': [{
                     'title': 'Duplicate object',
                     'description': 'Object already exists.'
                     }]
                 }],
             'internalErrorCode': 2002
         }
        }]
})

def get_object_id(obj_name, key, value):
    for object in database[obj_name]:
        if key in object:
            if object[key] == value:
                return object
    return {}


@app.route("/nuage/api/v1_0/me", methods=['GET'])
def me_show():
    reply = [{'firstName': 'csproot',
              'enterpriseName': 'CSP',
              'APIKey':'111-222-333',
              'APIKeyExpiry': (int(epoch())+100)*1000,
              'enterpriseID': '1234-5678-1234567890'}]
    return json.dumps(reply)


@app.route("/nuage/api/v1_0/enterprises", methods=['GET'])
def enterprises_list():
    return json.dumps(database['enterprises'])


@app.route("/nuage/api/v1_0/enterprises/1234-5678-1234567890", methods=['GET'])
def enterprises_show():
    return json.dumps([get_object_id('enterprises', 'ID', '1234-5678-1234567890')])


@app.route("/nuage/api/v1_0/enterprises", methods=['POST'])
def enterprises_create():
    data_update = json.loads(request.data)
    data_src = get_object_id('enterprises', 'name', data_update['name'])
    if len(data_src) != 0:
        return make_response(json.dumps(get_object_id('messages', 'name', 'already exists')['message']), '409')
    new = {'name': data_update['name'],
           'ID': '1111-2222-3333333333',
           'description': 'None'}
    database['enterprises'].append(new)
    return json.dumps([get_object_id('enterprises', 'ID', '1111-2222-3333333333')])

@app.route("/nuage/api/v1_0/enterprises/1234-5678-1234567890", methods=['PUT'])
def enterprises_update():
    data_update = json.loads(request.data)
    data_src = get_object_id('enterprises', 'ID', '1234-5678-1234567890')
    data_src.update(data_update)
    return '{}'

if __name__ == "__main__":
#    service.init()

    if '--debug' in sys.argv:
        app.debug = True
    app.run(host='0.0.0.0')
