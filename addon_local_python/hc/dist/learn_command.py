import os
from struct import pack
from const import ROOT_DIR, local_ip
import json
from websocket import create_connection
from utils import get_token, get_info_broadlink, get_model_broadlink, int_from_bytes
import requests
import broadlink
from broadlink.exceptions import check_error
import time
import base64


class Custom_rm(broadlink.rm):
    def check_data(self) -> bytes:
        packet = bytearray(self._request_header)
        packet.append(0x04)
        response = self.send_packet(0x6a, packet)
        try:
            check_error(response[0x22:0x24])
            payload = self.decrypt(response[0x38:])
            return payload[len(self._request_header) + 4:]
        except Exception as error:
            # print(error)
            pass


def learning_command_with_rf(mac, ip, model):
    # print('sending_the_call')
    device = sending_the_call(mac, ip, model)
    # print('step 1: pairing')

    if (pairing_frequency(device)):
        return 1
    else:
        return 0
    # step 2: learning -> learning_command_rf()
    # return device


def sending_the_call(mac, ip, model):
    if 'rm4' in model.split(" ")[0].lower():
        device = broadlink.rm4((ip, 80), mac, None)
    elif model == 'sp1':
        device = broadlink.sp1((ip, 80), mac, None)
    elif model == 'sp2':
        device = broadlink.sp2((ip, 80), mac, None)
    elif model == 'sp3':
        device = broadlink.sp3((ip, 80), mac, None)
    elif model == 'mp1':
        device = broadlink.mp1((ip, 80), mac, None)
    else:
        device = broadlink.rm((ip, 80), mac, None)
    device.auth()
    return device


def pairing_frequency(device):
    device.__class__ = Custom_rm
    device.sweep_frequency()
    found = device.check_frequency()
    # print("----------------------------\n\nkeep pushing button within about 30s\n\n----------------------------------\n")
    while found == False:
        found = device.check_frequency()
    return found


def learning_command(entity_id, command_type='ir') -> str:
    # get config_entry_id from entity_id with websocket
    if (command_type == 'ir'):
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
    else:
        name = entity_id.split('.')[1].split('_remote')[0]
        remote_data = get_info_broadlink(name)
        host = remote_data[0]['data']['host']
        mac = remote_data[0]['data']['mac']
        model = get_model_broadlink(name)
        return learning_command_with_rf(mac, host, model)


def learning_command_rf(mac, ip, model):
    device = sending_the_call(mac, ip, model)
    # print('step 2: learning')
    # print("----------------------------\n\npushing button to learning\n\n----------------------------------\n")
    device.__class__ = Custom_rm
    device.find_rf_packet()
    packet = device.check_data()
    cur = time.time()
    while packet == None:
        if time.time() - cur > 10:
            device.cancel_sweep_frequency()
            return None
        packet = device.check_data()
    command = base64.b64encode(packet).decode("utf8")
    device.cancel_sweep_frequency()
    return command


def learning_command_with_ir(entity_id, command_type='ir') -> str:
    if learning_command(entity_id, command_type=command_type):
        if check_broadlink_state(entity_id) == 'on':
            return(get_broadlink_remote_codes(entity_id))
        else:
            return ""


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

    response = requests.request(
        "GET", url, headers=headers, data=payload).json()
    return response['state']
