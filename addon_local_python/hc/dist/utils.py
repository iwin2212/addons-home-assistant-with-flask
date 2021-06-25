from websocket import create_connection
from flask import request
import requests
import json
from yaml_util import yaml2dict, dict2yaml
from const import ROOT_DIR, data_file
import os
from subprocess import Popen, PIPE, STDOUT
import zipfile
import shutil
import base64
import broadlink
from const import *
from os.path import basename
import logging

secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
URL_STATE = 'http://localhost:8123/api/states'
URL_SERVICE = 'http://localhost:8123/api/services'


def add_time(start_time, step_time, num):
    step_time = 60*int(step_time)*num
    if start_time.isdigit():
        start_time += ':00'
    start_time_split = start_time.split(":")
    start_time_in_minute = 60 * \
        int(start_time_split[0]) + int(start_time_split[1])
    result_time_in_minute = start_time_in_minute + step_time
    return str(result_time_in_minute // 60 % 24) + ":" + str(result_time_in_minute % 60)


def gen_climate_automation_content(name, entity_id, min_temp, max_temp, temp_step, start_time, step_time):
    num_of_automation = (max_temp - min_temp) // 2 + 1
    list_au = []
    for i in range(num_of_automation):
        data = {
            "alias": name + " " + str(min_temp) + str(max_temp) + add_time(start_time, step_time, i).split(":")[0],
            "id": "automation.bat_dieu_hoa_" + str(min_temp + i * temp_step) + "_" + add_time(start_time, step_time, i).split(":")[0],
            "trigger": [{
                "platform": "time",
                "at": add_time(start_time, step_time, i)
            }],
            "action": [
                {
                    "service": "climate.set_temperature",
                    "data": {
                        "entity_id": entity_id,
                        "temperature": min_temp + i * temp_step
                    }
                },
                {
                    "service": "climate.set_operation",
                    "data": {
                        "entity_id": entity_id,
                        "operation": "cool"
                    }
                }]
        }
        list_au.append(data)
    return list_au


def replace_space(string):
    if string.endswith(" "):
        string = string[0:len(string)-1]
    if string.startswith(" "):
        string = string[1:len(string)]
    string = string.replace(' ', '_')
    return string


def add_timestamp(iden):
    timestamp = iden.split(".")[-1]
    return str(int(timestamp) + 1)


def sub_timestamp(iden):
    timestamp = iden.split(".")[-1]
    return str(int(timestamp) - 1)


def sort_string_in_list_item(list_original):
    dict_medium = {}
    for i in list_original:
        dict_medium[i.split('(')[1].split(')')[0]] = i
    list_result = [value for (key, value) in sorted(dict_medium.items())]
    return list_result


def get_devices():
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    try:
        res = requests.get(URL_STATE, headers=headers)
        if res.status_code == 200:
            return res.json()
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None


def get_services():
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.get(URL_SERVICE, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        return None


def get_states(entity_id):
    URL = 'http://localhost:8123/api/states/{}'.format(entity_id)
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    try:
        res = requests.get(URL, headers=headers)
        if res.status_code == 200:
            response = json.loads(str(res.text).replace("\'", "\""))
            return response["state"]
        else:
            return None
    except requests.exceptions.ConnectionError:
        return None


def check_exist(path_file):
    if not os.path.exists(path_file):
        filename = path_file.split('/')[-1]
        if filename == 'xiaomi_aqara.yaml':
            dict2yaml({'gateways': []}, path_file)
        elif filename == 'light.yaml':
            dict2yaml({'devices': {}}, path_file)
        elif filename in ['configurator.yaml', 'input_boolean.yaml']:
            dict2yaml({}, path_file)
        elif filename == "device_tracker.yaml":
            dict2yaml(
                [{'platform': 'nmap_tracker', 'hosts': [], 'exclude': []}], path_file)
        else:
            dict2yaml([], path_file)
    else:
        content = yaml2dict(path_file)
        if str(content) == 'None':
            filename = path_file.split('/')[-1]
            if filename == 'xiaomi_aqara.yaml':
                dict2yaml({'gateways': []}, path_file)
            elif filename == 'light.yaml':
                dict2yaml({'devices': {}}, path_file)
            elif filename in ['configurator.yaml', 'input_boolean.yaml']:
                dict2yaml({}, path_file)
            elif filename == "device_tracker.yaml":
                dict2yaml(
                    [{'platform': 'nmap_tracker', 'hosts': [], 'exclude': []}], path_file)
            else:
                dict2yaml([], path_file)


def restart_automation():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://localhost:8123/api/services/automation/reload'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)


def read_list_channel():
    filename = os.path.join(data_file, 'list_channel.csv')
    file_ = open(filename, 'r')
    lines = file_.readlines()
    final_data = []
    for line in lines[1:]:
        final_data.append(line.split(","))
    return final_data


def check_in(list1, pos1, value):
    if value[0] == "_":
        for i in list1:
            if i[pos1].lower() == value[1:].lower():
                return True, list1.index(i)
    else:
        for i in list1:
            if i[pos1].lower() == value.lower():
                return True, list1.index(i)
    return False, -1


def get_command_line_result(command_line):
    out = Popen(command_line, stderr=STDOUT, stdout=PIPE)
    output = out.communicate()[0], out.returncode
    return output


def compress_data(zipfile_name, dir_):
    # shutil.make_archive(zipfile_name, 'zip', dir_)
    try:
        os.remove(zipfile_name)
    except:
        pass
    # copy all yaml file to a dir
    if not os.path.isdir(os.path.join(data_file, 'config_folder')):
        os.mkdir(os.path.join(data_file, 'config_folder'))
    list_file = os.listdir(dir_)
    for file_ in list_file:
        if file_.endswith('.yaml'):
            shutil.copyfile(os.path.join(dir_, file_), os.path.join(
                data_file, 'config_folder', file_))
    fantasy_zip = zipfile.ZipFile(zipfile_name, 'w')
    for file_ in os.listdir(os.path.join(data_file, 'config_folder')):
        if file_.endswith('.yaml'):
            # print(file_)
            fantasy_zip.write(os.path.join(dir_, file_),
                              basename(os.path.join(dir_, file_)))
    shutil.rmtree(os.path.join(data_file, 'config_folder'))
    fantasy_zip.close()


def unzip_file(filename, target_dir, config_dir):
    # unzip file config
    # print(target_dir)
    # print("====================================")
    with zipfile.ZipFile(filename, "r") as zip_ref:
        zip_ref.extractall(target_dir)

    for file_ in os.listdir(target_dir):
        # print(file_)
        if file_ != ".DS_Store":
            shutil.copyfile(os.path.join(target_dir, file_),
                            os.path.join(config_dir, file_))

    shutil.rmtree(target_dir)
    os.remove(filename)


def list_command_2_string(list_command, list_base_channel):
    string = ''
    for command in list_command:
        for base_channel in list_base_channel:
            if command == list_base_channel[base_channel]:
                string += str(base_channel[-1])
    return string


def code_2_command(code, data):
    list_ = []
    for i in code:
        list_.append(data['commands']['sources']['Channel ' + i])
    return list_


def get_new_channel(filename, channel_name, code):
    try:
        f = open(filename, 'r')
        data = json.load(f)
        f.close()
        result = code_2_command(code, data)
        if channel_name[0] == "_":
            if channel_name in data['commands']['sources']:
                del data['commands']['sources'][channel_name]
            if channel_name[1:] in data['commands']['sources']:
                del data['commands']['sources'][channel_name[1:]]
        else:
            if channel_name in data['commands']['sources']:
                del data['commands']['sources'][channel_name]
            if "_" + channel_name in data['commands']['sources']:
                del data['commands']['sources']["_" + channel_name]
        data['commands']['sources'][channel_name] = result
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        return True
    except:
        return False


def create_qr_data(path_file):
    f = open(path_file).read()
    return f


def from_entity_id_get_mac_ip(entity_id):
    # get config_entry_id from entity_id with websocket
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    string_web = "ws://"+local_ip+":8123/api/websocket"
    ws = create_connection(string_web)

    result = ws.recv()
    payload = {
        "type": "auth",
        "access_token": secret_data['token']
    }
    ws.send(json.dumps(payload))

    result = ws.recv()
    payload = {"type": "config/entity_registry/get",
               "entity_id": entity_id, "id": 1}
    ws.send(json.dumps(payload))

    result = ws.recv()
    data = json.loads(result)
    entry = (data['result']['config_entry_id'])
    # map config_entry_id - mac
    with open(os.path.join(ROOT_DIR, ".storage", "core.config_entries")) as json_file:
        config_entries_data = json.load(json_file)
    broadlink_device = [i for i in config_entries_data['data']
                        ['entries'] if (i['entry_id'] == entry)]
    # print(broadlink_device[0]['title'], broadlink_device[0]['data']['host'], broadlink_device[0]['data']['mac'])
    host = broadlink_device[0]['data']['host']
    mac = broadlink_device[0]['data']['mac']
    return mac, host


def from_mac_get_type(mac):
    with open(os.path.join(ROOT_DIR, ".storage", "core.config_entries")) as config_entries:
        config_entries_data = json.load(config_entries)
    for i in config_entries_data['data']['entries']:
        try:
            if (i['data']['mac'] == mac.lower()):
                entry = i['entry_id']
        except:
            pass

    with open(os.path.join(ROOT_DIR, ".storage", "core.device_registry")) as device_registry:
        config_device_data = json.load(device_registry)
    device = [i for i in config_device_data['data']
              ['devices'] if (entry in i['config_entries'])]
    type_ = device[0]['model']
    return type_


def get_broadlink_device_from_api():
    URL = 'http://'+local_ip+':8123/api/states'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.get(URL, headers=headers)
    list_broadlink = []
    if res.status_code == 200:
        response = json.loads(str(res.text))
        list_broadlink = [
            i for i in response if i['entity_id'].find('remote.') != -1]
    return list_broadlink


def sending_ir_packet(mac, ip, cmd):
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
    ir_packet = base64.b64decode(cmd)
    device.send_data(ir_packet)


def from_mac_get_entity_id(mac):
    with open(os.path.join(ROOT_DIR, ".storage", "core.config_entries")) as json_file:
        config_entries_data = json.load(json_file)
    for i in config_entries_data['data']['entries']:
        try:
            if (i['data']['mac'] == mac):
                entry_id = i['entry_id']
        except:
            pass
    return entry_id


def get_list_entity_id():
    list_entity_id = {}
    list_broadlink = get_broadlink_device_from_api()
    for broadlink in list_broadlink:
        mac, ip = from_entity_id_get_mac_ip(broadlink['entity_id'])
        list_entity_id[mac] = broadlink['entity_id']
    return list_entity_id


def broadlink_devices_info():
    list_mac = []
    list_host = []
    list_broadlink = get_broadlink_device_from_api()
    for boardlink in list_broadlink:
        entity_id = boardlink['entity_id']
        mac, host = from_entity_id_get_mac_ip(entity_id)
        list_mac.append(mac)
        list_host.append(host)
    return list_broadlink, list_mac, list_host


def check_tmp_camera_folder_exist():
    path_tmp = os.path.join(ROOT_DIR, "tmp/")
    if os.path.isdir(path_tmp) == False:
        os.mkdir(path_tmp)
    path_cam = os.path.join(ROOT_DIR, "tmp/camera/")
    if os.path.isdir(path_cam) == False:
        os.mkdir(path_cam)


def find_ip_broadlink():
    devices = broadlink.discover(timeout=5)
    info = str(devices).split("|")
    list_ip = [i.split("at ")[1].split(":")[0]
               for i in info if(i.find("at ") != -1)]
    list_broadlink, list_mac, list_host = broadlink_devices_info()
    list_ip = [i for i in list_ip if (i not in list_host)]
    return list_ip


def get_list_via_integration(*entity_type):
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    string_web = "ws://"+local_ip+":8123/api/websocket"
    ws = create_connection(string_web)
    result = ws.recv()

    payload = {
        "type": "auth",
        "access_token": secret_data['token']
    }
    ws.send(json.dumps(payload))
    result = ws.recv()

    payload = {"type": "config/entity_registry/list", "id": 1}
    ws.send(json.dumps(payload))
    result = ws.recv()
    entities = json.loads(result)['result']
    list_device = []
    for type_ in entity_type:
        list_device.extend([entity for entity in entities if (
            entity['platform'] == type_)])
    return list_device


def config_integration_device(entity_type, key, host, mac):
    secrets = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    token = secrets['token']
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
    url_flow = 'http://'+local_ip+':8123/api/config/config_entries/flow'
    payload = {
        "handler": entity_type,
        "show_advanced_options": True
    }
    res = requests.post(url_flow, data=json.dumps(payload), headers=headers)
    if res.status_code == 200:
        if (res.json()['type'] != 'abort'):
            flow_id = res.json()['flow_id']
            payload_2 = {}
            if (key != ''):
                payload_2['interface'] = 'any'
            if (host != ''):
                payload_2['host'] = host
            if (mac != ''):
                payload_2['mac'] = mac
            res = requests.post(url_flow + '/' + flow_id,
                                data=json.dumps(payload_2), headers=headers)
            if res.status_code == 200:
                if (key != ''):
                    payload_3 = {'name': "Xiaomi Aqara Gateway", 'key': key}
                    res = requests.post(url_flow + '/' + flow_id,
                                        data=json.dumps(payload_3), headers=headers)
                    if res.status_code == 200:
                        return {'error': False, 'data': res.json()}
                    else:
                        return {'error': res.json(), 'data': ''}
                else:
                    return {'error': False, 'data': res.json()}
            else:
                return {'error': res.json(), 'data': ''}
        else:
            return {'error': res.json(), 'data': ''}
    else:
        return {'error': res.json(), 'data': ''}


def config_integration_xiaomi(entity_type, key, host, name):
    secrets = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    token = secrets['token']
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }

    url_flow = "http://" + local_ip + ":8123/api/config/config_entries/flow"
    payload = {
        "handler": entity_type,
        "show_advanced_options": True
    }
    res = requests.post(url_flow, data=json.dumps(payload), headers=headers)
    if res.status_code == 200:
        if (res.json()['type'] != 'abort'):
            if (entity_type == 'xiaomi_miio'):
                url_flow = url_flow + '/' + res.json()['flow_id']
                res = requests.post(url_flow, data=json.dumps(
                    {"gateway": True}), headers=headers)
                try:
                    if (res.json()['step_id'] == 'gateway'):
                        payload_2 = {"name": name, "host": host, "token": key}
                        res = requests.post(url_flow, data=json.dumps(
                            payload_2), headers=headers)
                        if (res.json()['type'] != 'abort'):
                            return {'error': False, 'data': res.json()}
                        else:
                            return {'error': res.json(), 'data': ''}
                except:
                    payload_2 = {"host": host, "token": key}
                    res = requests.post(url_flow, data=json.dumps(
                        payload_2), headers=headers)
                    if (res.json()['type'] != 'abort'):
                        return {'error': False, 'data': res.json()}
                    else:
                        return {'error': res.json(), 'data': ''}
        else:
            return {'error': res.json(), 'data': ''}
    else:
        return {'error': res.json(), 'data': ''}


def get_config_entry_id(entity_id):
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    string_web = "ws://"+local_ip+":8123/api/websocket"
    ws = create_connection(string_web)
    result = ws.recv()
    payload = {
        "type": "auth",
        "access_token": secret_data['token']
    }
    ws.send(json.dumps(payload))
    result = ws.recv()

    payload = {"type": "config/entity_registry/list", "id": 1}
    ws.send(json.dumps(payload))
    result = ws.recv()
    entities = json.loads(result)['result']
    list_device = [entity for entity in entities if (
        entity['entity_id'] == entity_id)]
    if (list_device == []):
        return ''
    else:
        return list_device[0]['config_entry_id']


def delete_entity_via_integration(entity_type, entity_id):
    config_entry_id = get_config_entry_id(entity_id)
    if (config_entry_id == ''):
        return {'error': 'Không tìm thấy thiết bị này'}
    entity_id = request.args.get('id')
    #######################################
    secrets = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    token = secrets['token']
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
    URL = 'http://'+local_ip+':8123/api/config/config_entries/entry/'
    url_flow = URL + config_entry_id
    payload = {
        "handler": entity_type,
        "show_advanced_options": True
    }
    res = requests.delete(url_flow, data=json.dumps(payload), headers=headers)
    if res.status_code == 200:
        if (res.json()['require_restart'] == False):
            return {'error': False, 'require_restart': False}
        elif (res.json()['require_restart'] == True):
            return {'error': False, 'require_restart': True}
    else:
        return {'error': 'Lỗi kết nối đến thiết bị. Vui lòng kiểm tra lại đường truyền.'}


def deal_with_action():
    data = []
    list_delay = request.form.getlist('delay')
    list_entity = request.form.getlist('entity')
    list_action = request.form.getlist('action')
    count_loop = 0
    dem_tv = 0
    dem_tem = 0
    dem_mode = 0
    dem_fan_mode = 0
    dem_noi = 0
    # rèm
    dem_pct = 0
    # khoá
    dem_lock_code = 0
    # đèn
    dem_brightness_pct = 0
    dem_color = 0
    dem_profile = 0
    # thời gian chờ
    dem_delay = 0
    # media_player
    dem_vol = 0
    # camera
    dem_record_duration = 0
    list_duration = request.form.getlist('record_duration')

    # alarm
    dem_alarm_code = 0
    list_alarm_code = request.form.getlist('alarm_code')

    list_source = request.form.getlist('source')
    list_volume = request.form.getlist('volume')

    list_message = request.form.getlist('message')
    # climate
    list_temp = request.form.getlist('temperature')
    list_mode = request.form.getlist('mode')
    list_fan_mode = request.form.getlist('fan_mode')

    list_pct = request.form.getlist('pct_open')
    # khoá
    list_lock_code = request.form.getlist('lock_code')
    # list đèn
    list_brightness_pct = request.form.getlist(
        'brightness_pct')
    list_brightness_pct_order = request.form.getlist(
        'brightness_pct_order')
    list_color = request.form.getlist('color')
    list_color_order = request.form.getlist('color_order')
    list_profile = request.form.getlist('profile')
    list_profile_order = request.form.getlist('profile_order')
    # hành động xoá sẽ ảnh hưởng đến thứ tự của list các action của đèn
    # print("before: ", list_brightness_pct_order)
    del_action = request.form['del_act']
    if (del_action != ''):
        for i in del_action:
            for j in range(len(list_brightness_pct_order)):
                if (int(i) <= int(list_brightness_pct_order[j])):
                    list_brightness_pct_order[j] = str(
                        int(list_brightness_pct_order[j]) - 1)
        for i in del_action:
            for j in range(len(list_color_order)):
                if (int(i) <= int(list_color_order[j])):
                    list_color_order[j] = str(
                        int(list_color_order[j]) - 1)
        for i in del_action:
            for j in range(len(list_profile_order)):
                if (int(i) <= int(list_profile_order[j])):
                    list_profile_order[j] = str(
                        int(list_profile_order[j]) - 1)
    # list thời gian chờ
    list_delay = request.form.getlist('delay')
    # print(list_entity)
    for i, j in zip(list_entity, list_action):
        # print('-------------o0o----------------', i, j)
        count_loop += 1
        data.append({
            "delay": list_delay[count_loop-1]
        })
        # print('count_loop: ', count_loop-1)
        if (j.find('speak') != -1):
            data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
            ), 'message': list_message[dem_noi]}, "service": 'tts.google_translate_say'})
            dem_noi += 1
        elif j.find('media_player.select_source') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'source': list_source[dem_tv]},  "service": j})
            dem_tv += 1
        elif j.find('media_player.volume_set') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'volume_level': (int(list_volume[dem_vol])/100)},  "service": j})
            dem_vol += 1
        elif j.find('climate.set_temperature') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
            ), 'hvac_mode': list_mode[dem_mode], 'temperature': int(list_temp[dem_tem])},  "service": j})
            dem_tem += 1
            dem_mode += 1
        elif j.find('climate.set_fan_mode') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
            ), 'fan_mode': list_fan_mode[dem_fan_mode]},  "service": j})
            dem_fan_mode += 1
        elif j.find('set_cover_position') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
            ), 'position': int(list_pct[dem_pct])},  "service": j})
            dem_pct += 1
        elif j.find('lock') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'code': list_lock_code[dem_lock_code]},  "service": j})
            dem_lock_code += 1
        elif j.find('light.turn_on') != -1:
            set_mode = 0
            try:
                # print('try 1')
                if (int(list_brightness_pct_order[dem_brightness_pct]) == (count_loop - 1)):
                    # print('--------->brightness_pct')
                    data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                    ), 'brightness_pct': int(list_brightness_pct[dem_brightness_pct])},  "service": j})
                    dem_brightness_pct += 1
                    set_mode = 1
            except:
                try:
                    # print('try 2')
                    if (int(list_color_order[dem_color]) == (count_loop - 1)):
                        # print('--------->color')
                        data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                        ), 'color_name': list_color[dem_color]},  "service": j})
                        dem_color += 1
                        set_mode = 1
                except:
                    try:
                        # print('try 3')
                        if (int(list_profile_order[dem_profile]) == (count_loop - 1)):
                            # print('--------->profile')
                            data.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                            ), 'profile': list_profile[dem_profile]},  "service": j})
                            dem_profile += 1
                            set_mode = 1
                    except:
                        pass
                        # print('else')
            if (set_mode == 0):
                data.append({"data": {"entity_id": i.split(
                    '(')[1].replace(')', '').strip()},  "service": j})
        elif j.find('alarm_control_panel') != -1:
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'code': int(list_alarm_code[dem_alarm_code])},  "service": j})
            dem_alarm_code += 1
        elif j.find('camera.record') != -1:
            check_tmp_camera_folder_exist()
            video_dir = "tmp/camera/record_{{ now().strftime('%Y%m%d-%H%M%S') }}.mp4"
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'filename': video_dir, 'duration': list_duration[dem_record_duration]},  "service": j})
            dem_record_duration += 1
        elif j.find('camera.snapshot') != -1:
            check_tmp_camera_folder_exist()
            image_dir = "tmp/camera/snapshot_{{ now().strftime('%Y%m%d-%H%M%S') }}.jpg"
            data.append({"data": {"entity_id": i.split('(')[1].replace(
                ')', '').strip(), 'filename': image_dir},  "service": j})
        else:
            data.append({"data": {"entity_id": i.split(
                '(')[1].replace(')', '').strip()},  "service": j})
    return data


def deal_with_trigger():
    data = []
    list_trigger = request.form.getlist('trigger')
    list_state = request.form.getlist('trigger_state')
    list_trigger_above = request.form.getlist('trigger_above')
    list_trigger_below = request.form.getlist('trigger_below')
    list_trigger_fromstate = request.form.getlist(
        'trigger_fromstate')
    list_state_condition = request.form.getlist(
        'condition_state')
    list_trigger_tostate = request.form.getlist(
        'trigger_tostate')
    list_trigger_time = request.form.getlist('trigger_time')
    count_trigger_sensor = 0
    count_trigger_other_device = 0
    for i in range(len(list_trigger)):
        trigger = list_trigger[i].split("(")[1][:-1]
        if list_state[i] == "So sánh":
            dict_in_data = {
                'platform': 'numeric_state',
                'entity_id': trigger,
                'for': list_trigger_time[i] if list_trigger_time[i] != "" else '00:00:00'
            }
            try:
                if list_trigger_above[count_trigger_sensor] != '':
                    dict_in_data['above'] = int(
                        list_trigger_above[count_trigger_sensor])
            except:
                pass
            try:
                if list_trigger_below[count_trigger_sensor] != '':
                    dict_in_data['below'] = int(
                        list_trigger_below[count_trigger_sensor])
            except:
                pass
            data.append(dict_in_data)
            count_trigger_sensor += 1
        else:
            dict_in_data = {
                'platform': 'state',
                'entity_id': trigger,
                'for': list_trigger_time[i] if list_trigger_time[i] != "" else '00:00:00'
            }
            try:
                if list_trigger_fromstate[count_trigger_other_device] != '':
                    dict_in_data['from'] = list_trigger_fromstate[count_trigger_other_device].lower(
                    )
            except:
                pass
            try:
                if list_trigger_tostate[count_trigger_other_device] != '':
                    dict_in_data['to'] = list_trigger_tostate[count_trigger_other_device].lower(
                    )
            except:
                pass
            data.append(dict_in_data)
            count_trigger_other_device += 1
    return data


def deal_with_condition():
    data = []
    list_condition = request.form.getlist('condition')
    list_condition_state = request.form.getlist(
        'condition_state')
    list_chose_condition_state = request.form.getlist(
        'chose_condition_state')
    list_condition_above = request.form.getlist(
        'above_condition')
    list_condition_below = request.form.getlist(
        'below_condition')
    count_condition_sensor = 0
    count_condition_other_device = 0
    try:
        after = str(request.form["after"])
        before = str(request.form["before"])
        if after == "":
            if before != "":
                data.append({
                    "condition": "time",
                    "before": before if before != "24:00" else "00:00"
                })
        else:
            if before == "":
                data.append({
                    "condition": "time",
                    "after": after if after != "24:00" else "00:00"
                })
            else:
                data.append({
                    "condition": "time",
                    "after": after if after != "24:00" else "00:00",
                    "before": before if before != "24:00" else "00:00"
                })
    except:
        pass
    for i in range(len(list_condition)):
        condition = list_condition[i].split("(")[1][:-1]
        if list_chose_condition_state[i] == "So sánh":
            data.append({
                "entity_id": condition,
                "condition": "numeric_state",
                "above": list_condition_above[count_condition_sensor] if list_condition_above[count_condition_sensor] != "" else None,
                "below": list_condition_below[count_condition_sensor] if list_condition_below[count_condition_sensor] != "" else None
            })
            count_condition_sensor += 1
        else:
            data.append({
                "entity_id": condition,
                "condition": "state",
                "state": list_condition_state[count_condition_other_device].lower() if len(list_condition_state) != 0 else ""
            })
            count_condition_other_device += 1
    return data


def load_ircode():
    ircode_path = os.path.join(data_file, 'ircode.json')
    with open(ircode_path) as json_file:
        IR_CODE = json.load(json_file)
    return IR_CODE


def write_ircode(IR_CODE):
    ircode_path = os.path.join(data_file, 'ircode.json')
    with open(ircode_path, 'w') as outfile:
        json.dump(IR_CODE, outfile, indent=4)


def file_existed(path) -> bool:
    return os.path.isfile(path)


def get_token():
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    return secret_data['token']


def get_info_broadlink(name) -> dict:
    with open(os.path.join(ROOT_DIR, ".storage", "core.config_entries")) as json_file:
        config_entries = json.load(json_file)['data']['entries']
    try:
        data = [device for device in config_entries if device["domain"]
                == "broadlink" and device["title"] == name]
        return data
    except Exception as error:
        print(error)
        return


def get_model_broadlink(name) -> dict:
    with open(os.path.join(ROOT_DIR, ".storage", "core.device_registry")) as json_file:
        devices_data = json.load(json_file)['data']['devices']
    try:
        model = [device for device in devices_data if "broadlink" in device["identifiers"]
                 [0] and device["name"] == name][0]['model']
        return model
    except:
        return


# int to bytes && vice versa
def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')


def get_info_dev(ip):
    try:
        url = "http://"+ip+"/api/info"

        payload = ""
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiI1YTg4NGFiZmZlMTU0MDM3OGUyYzBkYjhkMzhlM2IyNCIsImlhdCI6MTYyMjM4NjU0OSwiZXhwIjoxOTM3NzQ2NTQ5fQ.nsHUhjshUyBq4qxLFZPa_pPvBh_M_Fw-K7hYkjyVv78',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return (response.json())
    except Exception as error:
        return {"error": str(error)}


def get_javis_dev():
    try:
        with open(os.path.join(data_file, "javishome_device.json")) as json_file:
            return json.load(json_file)
    except:
        return []


def write_javis_dev(javis_dev):
    with open(os.path.join(data_file, "javishome_device.json"), 'w') as json_file:
        json.dump(javis_dev, json_file, indent=4)


if __name__ == "__main__":
    compress_data("c.zip", "config_folder")
