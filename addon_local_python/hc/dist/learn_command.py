import os
from const import ROOT_DIR, local_ip
import json
from websocket import create_connection
from utils import get_token
import requests


def learning_command_rf(entity_id, command_type='rf') -> str:
    if learning_command(entity_id, command_type=command_type):
        return(get_broadlink_remote_codes(entity_id))


def learning_command_with_ir(entity_id, command_type='ir') -> str:
    if learning_command(entity_id, command_type=command_type):
        if check_broadlink_state(entity_id) == 'on':
            return(get_broadlink_remote_codes(entity_id))
        else:
            return ""


def learning_command(entity_id, command_type='ir') -> str:
    # get config_entry_id from entity_id with websocket

    string_web = "ws://"+local_ip+":8123/api/websocket"
    ws = create_connection(string_web)
    result = ws.recv()

    payload = {
        "type": "auth",
        "access_token": get_token()
    }
    ws.send(json.dumps(payload))
    result = ws.recv()

    payload = json.dumps({"type": "execute_script", "sequence": [{"service": "remote.learn_command", "data": {
                         "device": "learning_command", "command": "learn_via_ws", "command_type": command_type, "timeout": 30, "entity_id": entity_id}}], "id": 32})
    ws.send(payload)
    result = ws.recv()
    return json.loads(result)['success']


def get_mac_from_entity_id(entity_id) -> str:
    with open(os.path.join(ROOT_DIR, ".storage", "core.entity_registry")) as json_file:
        config_entries_data = json.load(json_file)

    entries = config_entries_data['data']['entities']
    broadlink_remote = [entry for entry in entries if (
        entity_id == entry['entity_id'])][0]

    return broadlink_remote['unique_id']


def get_broadlink_remote_codes(entity_id):
    mac = get_mac_from_entity_id(entity_id)
    database_path = os.path.join(ROOT_DIR, '.storage')
    for root, dirs, files in os.walk(database_path, topdown=False):
        broadlink_file = [f for f in files if (mac+"_codes" in f)][0]

    with open(os.path.join(root, broadlink_file)) as json_file:
        data = json.load(json_file)['data']['learning_command']['learn_via_ws']
    return data


def check_broadlink_state(entity_id):
    url = "http://"+local_ip+":8123/api/states/{}".format(entity_id)
    payload = ""
    headers = {
        'Authorization': "Bearer " + get_token()
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()
    return response['state']
