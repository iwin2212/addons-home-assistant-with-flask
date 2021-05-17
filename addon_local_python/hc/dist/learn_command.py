import requests
from const import ROOT_DIR
from yaml_util import yaml2dict
import os
import json
import time
import broadlink
import base64
from broadlink.exceptions import check_error
from utils import from_mac_get_type


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


def learning_command_with_rf(mac, ip):
    # print('sending_the_call')
    device = sending_the_call(mac, ip)
    # print('step 1: pairing')

    if (pairing_frequency(device)):
        return 1
    else:
        return 0
    # step 2: learning -> learning_command_rf()
    # return device


def sending_the_call(mac, ip):
    os.path.join(ROOT_DIR, 'switch.yaml')
    type_ = from_mac_get_type(mac).lower()
    # print(type_)
    if 'rm4' in type_:
        device = broadlink.rm4((ip, 80), mac, None)
    elif type_ == 'sp1':
        device = broadlink.sp1((ip, 80), mac, None)
    elif type_ == 'sp2':
        device = broadlink.sp2((ip, 80), mac, None)
    elif type_ == 'sp3':
        device = broadlink.sp3((ip, 80), mac, None)
    elif type_ == 'mp1':
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


def learning_command_rf(mac, ip):
    device = sending_the_call(mac, ip)
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


def learning_command_with_ir(mac, ip):
    device = sending_the_call(mac, ip)
    device.__class__ = Custom_rm
    # packet = custom_check_data(device)
    device.enter_learning()
    packet = device.check_data()
    cur = time.time()
    while packet == None:
        if time.time() - cur > 10:
            device.cancel_sweep_frequency()
            return None
        device.enter_learning()
        packet = device.check_data()
    data = base64.b64encode(packet).decode("utf8")
    device.cancel_sweep_frequency()
    return data


def inspect_type(id_addr):
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    devices = yaml2dict(filename)
    for device in devices:
        try:
            if device['host'] == id_addr:
                device_type = device['type']
        except Exception as error:
            continue
    return device_type


URL_call = 'http://localhost:8123/api/services/broadlink/learn'
URL_states = 'http://localhost:8123/api/states'


def get_password():
    filename = os.path.join(ROOT_DIR, 'secrets.yaml')
    secret_data = yaml2dict(filename)
    return secret_data['token']


def call_service(ip):
    pwd = get_password()
    res = requests.post(URL_call, data=str({"host": ip}).replace("\'", "\"").encode(
    ), headers={'Authorization': 'Bearer ' + pwd, 'content-type': 'application/json'})
    if res.status_code == 200:
        return True
    return False


def get_states():
    pwd = get_password()
    res = requests.get(URL_states, headers={
                       'Authorization': 'Bearer ' + pwd, 'content-type': 'application/json'})
    data = json.loads(res.text.replace("\'", "\""))
    return data


def get_signal(ip):
    pwd = get_password()
    old_res = requests.get(URL_states, headers={
                           'Authorization': 'Bearer ' + pwd, 'content-type': 'application/json'})
    # print(old_res.status_code)
    old_data = json.loads(old_res.text.replace("\'", "\""))
    if call_service(ip) == False:
        # print("Không kích hoạt được chức năng học lệnh")
        return None
    # print("Chờ người dùng bấm lệnh.........")
    curr = time.time()
    command = None
    while True:
        if time.time() - curr > 20:
            break
        res = requests.get(URL_states, headers={
                           'Authorization': 'Bearer ' + pwd, 'content-type': 'application/json'})
        data = json.loads(res.text.replace("\'", "\""))
        for device in data:
            if device['entity_id'].find('persistent_notification.notification') != -1 and device not in old_data:
                # print(device['entity_id'])
                command = device['attributes']['message']
        if command != None:
            break

    if command == None or command == "Did not received any signal":
        # print("Khong nhan duoc tin hieu")
        return None
    return command.split(":")[-1].strip()


if __name__ == "__main__":
    # ip = '192.168.31.28'
    # print(get_signal(ip))
    iden = '24:DF:A7:F1:04:EA'
    # print(learning_command_with_ir(iden))
    # print("method: ", learning_command_with_rf(iden))
