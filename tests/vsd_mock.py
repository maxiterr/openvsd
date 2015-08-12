import sys
from flask import Flask, request, make_response
import json
from time import time as epoch

app = Flask(__name__)

database = {}
database.update(
    {
        'enterprises':  [
            {
                'ID': '92a76e6f-2ac4-43f2-8c1f-a052c5f4d90e',
                'name': 'nulab-1',
                'description': 'None',
                'parentType': 'null',
                'enterpriseProfileID': 'd63701e0-9246-4c7a-9f43-0c66d0fe45e3'
            },
            {
                'ID': '5b2cc2f3-2b86-42ec-892d-edde741b2fd4',
                'name': 'nulab-2',
                'description': 'None',
                'parentType': 'null',
                'enterpriseProfileID': '3e05994c-0f9b-41d0-84d5-ec083ee89567'
            }
        ]
    }
)
database.update(
    {
        'messages':  [
            {
                'name': 'already exists',
                'message':  {
                    'errors':  [
                        {
                            'property': 'name',
                            'descriptions':  [
                                {
                                    'title': 'Duplicate object',
                                    'description': 'Object already exists.'
                                }
                            ]
                        }
                    ],
                    'internalErrorCode': 2002
                }
            }
        ]
    }
)


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
              'APIKey':'02a99c64-a09a-46d7',
              'APIKeyExpiry': (int(epoch())+100)*1000,
              'enterpriseID': 'fc3a351e-87dc-46a4-bcf5-8c4bb204bd46'}]
    return json.dumps(reply)


@app.route("/nuage/api/v1_0/<obj_name>", methods=['GET'])
def enterprises_list(obj_name):
    return json.dumps(database[obj_name])


@app.route("/nuage/api/v1_0/enterprises/<ent_id>", methods=['GET'])
def enterprises_show(ent_id):
    return json.dumps([get_object_id('enterprises', 'ID', ent_id)])


@app.route("/nuage/api/v1_0/enterprises", methods=['POST'])
def enterprises_create():
    data_update = json.loads(request.data)
    data_src = get_object_id('enterprises', 'name', data_update['name'])
    if len(data_src) != 0:
        return make_response(json.dumps(
            get_object_id('messages', 'name', 'already exists')['message']), '409')
    new = {'name': data_update['name'],
           'ID': '255d9673-7281-43c4-be57-fdec677f6e07',
           'description': 'None'}
    database['enterprises'].append(new)
    return json.dumps([get_object_id('enterprises', 'ID', '255d9673-7281-43c4-be57-fdec677f6e07')])


@app.route("/nuage/api/v1_0/enterprises/<ent_id>", methods=['PUT'])
def enterprises_update():
    data_update = json.loads(request.data)
    data_src = get_object_id('enterprises', 'ID', ent_id)
    data_src.update(data_update)
    return '{}'


if __name__ == "__main__":
    if '--debug' in sys.argv:
        app.debug = True
    app.run(host='127.0.0.1')
