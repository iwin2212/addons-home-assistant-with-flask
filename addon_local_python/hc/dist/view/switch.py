from flask import render_template, request, session, jsonify, Blueprint
from yaml_util import yaml2dict, dict2yaml
from utils import *
import json
from const import *
import os
import requests
import threading
import re
import socket
import time
from wifi_connector import *
mod = Blueprint('switch', __name__)


# xoa cac thiet bi sensor, climate, media
# @mod.route('/delete_device', methods=['POST'])
# def remove_device():
#     item = request.args.get("item")
#     mac = request.args.get("mac")
#     if request.method == 'POST':
#         filename = os.path.join(ROOT_DIR, item + '.yaml')
#         list_device = yaml2dict(filename)
#         devices = []
#         for i in list_device:
#             if 'mac' in i.keys():
#                 if i['mac'] != mac:
#                     devices.append(i)
#             else:
#                 devices.append(i)
#         list_device = devices
#         dict2yaml(list_device, filename)
#         if item == 'climate':
#             pre_url = 'air_condition' + '.'
#         elif item == 'sensor' or item == 'media':
#             pre_url = item + '.'
#         else:
#             pre_url = ''
#         return redirect(url_for(pre_url+'show_' + item))


@mod.route('/switch_broadlink')
def show_broadlink_switch():
    try:
        info = request.args.get('info')
        eth0 = request.args.get('eth0')
        if info != None:
            info = "Thêm thiết bị thành công."
        list_broadlink = get_broadlink_device_from_api()
        return render_template('./broad_link/switch_broadlink.html', info=info, list_broadlink=list_broadlink, eth0=eth0)
    except Exception as err:
        print(err)
        return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')


@mod.route('/show_fully_broadlink')
def show_fully_broadlink():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                info = request.args.get('info')
                if info != None:
                    info = "Thêm thiết bị thành công."
                items = []
                filename = os.path.join(ROOT_DIR, 'switch.yaml')
                check_exist(filename)
                list_device = yaml2dict(filename)
                list_device = [
                    i for i in list_device if i['platform'] == 'broadlink']
                for i in list_device:
                    items.append(i)
                list_entity_id = get_list_entity_id()
                return render_template('./broad_link/fully_broadlink_devices.html', items=items, list_entity_id=list_entity_id, info=info)
            except:
                return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/get_mqtt_info')
def get_mqtt_info():
    try:
        ip = request.args.get('ip')
        res = requests.get('http://' + ip + '/api/info')
        return res.text
    except:
        return "Không kết nối được IP"


@mod.route('/add_mqtt')
def add_mqtt():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            try:
                mqtt = os.path.join(data_file, 'mqtt.json')
                with open(mqtt) as json_file:
                    data = json.load(json_file)
                return render_template('./switch_mqtt/add_mqtt.html', err='', success='', data=data)
            except Exception as error:
                err = error
                return render_template('./switch_mqtt/add_mqtt.html', err=err, success='')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_mqtt', methods=['POST'])
def add_switch_result():
    if request.method == 'POST':
        # print(request.form)
        ip = request.form['ip']
        try:
            response = requests.get(
                'http://' + ip + '/api/info', timeout=15)
        except:
            err = 'Không kết nối được với địa chỉ ' + ip + ", xin kiểm tra lại thông tin"
            return render_template('./switch_mqtt/add_mqtt.html', err=err, success='')

        data = response.json()
        model = data['model']
        netid = data['netid']
        # print(data)
        # them mqtt device vao danh sach tham chieu
        mqtt_reference_file = os.path.join(ROOT_DIR, 'mqtt.yaml')
        mqtt_reference_data = yaml2dict(mqtt_reference_file)

        # load danh sach device
        filename = os.path.join(ROOT_DIR, 'switch.yaml')
        mqtt_data = yaml2dict(filename)
        mqtt = os.path.join(data_file, 'mqtt.json')
        with open(mqtt) as json_file:
            data_ = json.load(json_file)
        number_of_channel = data_[model]
        adding_data = {
            "platform": "mqtt",
            "ip": request.form["ip"],
            "netid": netid,
            "n_switch": number_of_channel
        }
        if adding_data in mqtt_reference_data:
            return render_template('./switch_mqtt/add_mqtt.html', err="Bộ công tắc đã được thêm trước đó", success='')
        mqtt_reference_data.append(adding_data)
        dict2yaml(mqtt_reference_data, mqtt_reference_file)
        print(range(number_of_channel))
        for it in range(number_of_channel):
            config_data = {
                "platform": "mqtt",
                "name": request.form["congtac" + str(it + 1)],
                "state_topic": str(netid) + "/switch." + str(it + 1) + "/state",
                "command_topic": str(netid) + "/switch." + str(it + 1) + "/set",
                "payload_on": "on",
                "payload_off": "off",
                "state_on": "on",
                "state_off": "off"
            }
            mqtt_data.append(config_data)
        dict2yaml(mqtt_data, filename)
        return show_mqtt()


@mod.route('/add_mqtt_cover', methods=['GET', 'POST'])
def add_mqtt_cover():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                return render_template('./switch_mqtt/add_mqtt_cover.html', err='', success='')
            else:
                ip = request.form['ip']
                try:
                    response = requests.get(
                        'http://' + ip + '/api/info', timeout=15)
                except:
                    err = 'Không kết nối được với địa chỉ ' + ip + ", xin kiểm tra lại thông tin"
                    return render_template('./switch_mqtt/add_mqtt.html', err=err, success='')

                data = json.loads(str(response.text).replace("\'", "\""))
                netid = data['netid']
                data = {
                    "platform": "mqtt",
                    "name": request.form["name"],
                    "command_topic": netid + "/curtain.1/set",
                    "position_topic": netid + "/curtain.1/position",
                    "set_position_topic": netid + "/curtain.1/set_position",
                    "payload_open": "open",
                    "payload_close": "close",
                    "payload_stop": "stop",
                    "position_open": 5,
                    "position_closed": 96
                }
                list_cover = yaml2dict(os.path.join(
                    ROOT_DIR, 'dooya_cover.yaml'))
                list_cover.append(data)
                dict2yaml(list_cover, os.path.join(
                    ROOT_DIR, 'dooya_cover.yaml'))
                return show_dooya_cover()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/delete_mqtt_cover', methods=['POST'])
def delete_mqtt_cover():
    if 'logged_in' in session:
        if session['logged_in']:
            netid = request.args.get('netid')
            list_cover = yaml2dict(os.path.join(ROOT_DIR, 'dooya_cover.yaml'))
            new_list_cover = [i for i in list_cover if 'command_topic' not in i] + \
                [i for i in list_cover if 'command_topic' in i if i['command_topic'].split(
                    "/")[0] != netid]
            dict2yaml(new_list_cover, os.path.join(
                ROOT_DIR, 'dooya_cover.yaml'))
            info = "Đã xoá thiết bị thành công."
            list_dooya = yaml2dict(os.path.join(ROOT_DIR, 'dooya_cover.yaml'))
            return render_template('./dooya_cover/dooya_cover.html', list_dooya=list_dooya, info=info)


@mod.route('/delete_mqtt_dooya', methods=['POST'])
def delete_mqtt_dooya():
    if 'logged_in' in session:
        if session['logged_in']:
            mac = request.args.get('mac')
            list_cover = yaml2dict(os.path.join(ROOT_DIR, 'dooya_cover.yaml'))
            new_list_cover = [i for i in list_cover if (i['mac'] != mac)]
            dict2yaml(new_list_cover, os.path.join(
                ROOT_DIR, 'dooya_cover.yaml'))
            info = "Đã xoá thiết bị thành công."
            list_dooya = yaml2dict(os.path.join(ROOT_DIR, 'dooya_cover.yaml'))
            return render_template('./dooya_cover/dooya_cover.html', list_dooya=list_dooya, info=info)


@mod.route('/add_switch_rf')
def add_switch_rf():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            entity_id = request.args.get('entity_id')
            list_broadlink, list_mac, list_host = broadlink_devices_info()
            list_mini_devices = []
            for mac in list_mac:
                type_ = from_mac_get_type(mac)
                if ("mini" in type_):
                    list_mini_devices.append(mac)
            return render_template('./broad_link/add_switch_rf.html', entity_id=entity_id, list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host, list_mini_devices=list_mini_devices)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/pairing_rf', methods=['POST'])
def pairing_rf():
    mac = request.args.get('mac')
    ip = request.args.get('host')
    p = learning_command_with_rf(mac, ip)
    return jsonify(result=p)


@mod.route('/add_switch_rf', methods=['POST'])
def add_switch_rf_handler():
    mac = request.args.get('mac')
    mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + \
        ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12]
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    list_switch_hub = yaml2dict(filename)
    find_mac = 0
    switch_data = {
        "name": request.form["name"],
        "command_on": request.form["command_on"],
        "command_off": request.form["command_off"]
    }
    for switch in list_switch_hub:
        if (switch.get('mac') == mac):
            find_mac = 1
            # xử lý với trường hợp các bộ HC chạy theo kiểu cũ
            if (str(type(switch["switches"])) == "<class 'dict'>"):
                switch["switches"] = [switch_data]
            ##################################
            else:
                switch["switches"].append(switch_data)
    if find_mac == 0:
        data = {}
        data['mac'] = mac
        data['platform'] = "broadlink"
        data["switches"] = []
        data["switches"].append(switch_data)
        list_switch_hub.append(data)
    dict2yaml(list_switch_hub, filename)
    return show_fully_broadlink()


@mod.route('/add_switch_co_san')
def add_switch_co_san():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            entity_id = request.args.get('entity_id')
            list_broadlink, list_mac, list_host = broadlink_devices_info()
            return render_template('./broad_link/add_switch_co_san.html', entity_id=entity_id, list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_switch_co_san', methods=['POST'])
def add_switch_co_san_handler():
    mac = request.args.get('mac')
    mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + \
        ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12]
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    list_switch_hub = yaml2dict(filename)
    # print(request.form)
    find_mac = 0
    switch_data = {
        "name": request.form["name"],
        "command_on": request.form["command_on"],
        "command_off": request.form["command_off"]
    }
    for switch in list_switch_hub:
        if (switch.get('mac') == mac):
            find_mac = 1
            # xử lý với trường hợp các bộ HC chạy theo kiểu cũ
            if (str(type(switch["switches"])) == "<class 'dict'>"):
                switch["switches"] = [switch_data]
            ##################################
            else:
                switch["switches"].append(switch_data)
    if find_mac == 0:
        data = {}
        data['mac'] = mac
        data['platform'] = "broadlink"
        data["switches"] = []
        data["switches"].append(switch_data)
        list_switch_hub.append(data)
    dict2yaml(list_switch_hub, filename)
    return show_fully_broadlink()


@mod.route('/show_mqtt')
def show_mqtt_device():
    if 'logged_in' in session:
        if session['logged_in']:
            netid = request.args.get('netid')
            file_switch = os.path.join(ROOT_DIR, 'switch.yaml')
            check_exist(file_switch)
            list_mqtt_device = [i for i in yaml2dict(
                file_switch) if i['platform'] == 'mqtt']
            mqtt_device = []
            for dev in list_mqtt_device:
                if dev['state_topic'].find(netid) != -1:
                    mqtt_device.append(dev)
            return render_template('./switch_mqtt/mqtt.html', list_mqtt=mqtt_device)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/delete_device_mqtt', methods=['POST'])
def remove_mqtt():
    netid = request.args.get("netid")
    if request.method == 'POST':
        list_device = yaml2dict(os.path.join(ROOT_DIR, 'switch.yaml'))
        list_dev = yaml2dict(os.path.join(ROOT_DIR, 'mqtt.yaml'))
        list_dev = [i for i in list_dev if i['netid'] != netid]
        list_dev_final = []
        for i in list_device:
            if i['platform'] == 'mqtt':
                try:
                    if i['state_topic'].find(netid) == -1:
                        list_dev_final.append(i)
                except Exception as error:
                    continue
            else:
                list_dev_final.append(i)
        dict2yaml(list_dev, os.path.join(ROOT_DIR, 'mqtt.yaml'))
        dict2yaml(list_dev_final, os.path.join(ROOT_DIR, 'switch.yaml'))
        return show_mqtt()


@mod.route('/show_broadlink')
def show_broadlink():
    entity_id = request.args.get('entity_id')
    mac, host = from_entity_id_get_mac_ip(entity_id)
    try:
        type_ = from_mac_get_type(mac)
    except:
        type_ = ''
    mac = mac[0:2] + ':' + mac[2:4] + ':' + mac[4:6] + \
        ':' + mac[6:8] + ':' + mac[8:10] + ':' + mac[10:12]
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    check_exist(filename)
    list_device = yaml2dict(filename)
    item = ''
    try:
        list_device = [
            i for i in list_device if i['platform'] == 'broadlink']
        for i in list_device:
            if i['mac'].lower() == mac:
                item = i
                break
            else:
                item = ''
    except:
        item = ''
    return render_template('./broad_link/broadlink_devices.html', hub=item, entity_id=entity_id, host=host, mac=mac, type_=type_)


@mod.route('/delete_device_broadlink', methods=['POST'])
def rm_broadlink():
    entity_id = request.args.get("entity_id")
    mac, host = from_entity_id_get_mac_ip(entity_id)

    list_switch = yaml2dict(os.path.join(ROOT_DIR, 'switch.yaml'))
    mqtt_switch = [i for i in list_switch if i['platform'] == 'mqtt']
    new_broadlink_switch = [
        i for i in list_switch if 'mac' in i and i['mac'] != mac]
    mqtt_switch.extend(new_broadlink_switch)
    dict2yaml(mqtt_switch, os.path.join(ROOT_DIR, 'switch.yaml'))
    return show_broadlink_switch()


@mod.route('/delete_device_broadlink_with_mac', methods=['POST'])
def remove_broadlink():
    mac = request.args.get("mac")
    iden = request.args.get("iden")
    list_device = yaml2dict(os.path.join(ROOT_DIR, 'switch.yaml'))
    list_device_broadlink = [
        i for i in list_device if i['platform'] == 'broadlink']
    list_device_mqtt = [i for i in list_device if i['platform'] != 'broadlink']
    for item in list_device_broadlink:
        if item['mac'] == mac:
            len_data = (len(item['switches']))
            for i in range(len_data):
                try:
                    if (item['switches'][i]['name'] == iden):
                        del item['switches'][i]
                        break
                except:
                    del item['switches'][iden]
                    break
    dict2yaml(list_device_broadlink + list_device_mqtt,
              os.path.join(ROOT_DIR, 'switch.yaml'))
    return show_fully_broadlink()


@mod.route('/broadlink_configration', methods=['GET', 'POST'])
def broadlink_configration():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                wifi_list, signal_list, security_list = get_wifi_list()
                try:
                    ip = get_ip_from_wifi_connected()
                except:
                    ip = ''
                return render_template('./broad_link/broadlink_config.html', wifi_list=wifi_list, ip=ip)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/configure_broadlink', methods=['GET', 'POST'])
def configure_broadlink():
    ssid = request.args.get('ssid')
    pwd = request.args.get('pwd')
    setup(ssid, pwd, 3)
    devices = broadlink.discover(timeout=5)
    try:
        return jsonify(devices=devices)
    except Exception as error:
        return jsonify(error=error)


def setup(ssid: str, password: str, security_mode: int) -> None:
    """Set up a new Broadlink device via AP mode."""
    # Security mode options are (0 - none, 1 = WEP, 2 = WPA1, 3 = WPA2, 4 = WPA1/2)
    payload = bytearray(0x88)
    payload[0x26] = 0x14  # This seems to always be set to 14
    # Add the SSID to the payload
    ssid_start = 68
    ssid_length = 0
    for letter in ssid:
        payload[(ssid_start + ssid_length)] = ord(letter)
        ssid_length += 1
    # Add the WiFi password to the payload
    pass_start = 100
    pass_length = 0
    for letter in password:
        payload[(pass_start + pass_length)] = ord(letter)
        pass_length += 1

    payload[0x84] = ssid_length  # Character length of SSID
    payload[0x85] = pass_length  # Character length of password
    payload[0x86] = security_mode  # Type of encryption

    checksum = sum(payload, 0xbeaf) & 0xffff
    payload[0x20] = checksum & 0xff  # Checksum 1 position
    payload[0x21] = checksum >> 8  # Checksum 2 position
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(payload, ('255.255.255.255', 80))
    sock.close()


@mod.route('/add_broadlink', methods=['GET', 'POST'])
def add_broadlink():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                return render_template('./broad_link/add_broadlink.html')
            else:
                return show_broadlink_switch()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/find_broadlink', methods=['POST', 'GET'])
def find_broadlink():
    if 'logged_in' in session:
        if session['logged_in']:
            list_ip = find_ip_broadlink()
            return jsonify(list_ip=list_ip)
    else:
        return render_template('./login.html')


@mod.route('/connect_broadlink', methods=['POST'])
def connect_broadlink():
    ip = request.args.get('ip')
    timeout = request.args.get('timeout')
    name_devices = request.args.get('name_devices')

    secrets = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    token = secrets['token']
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
    url_flow = 'http://'+local_ip+':8123/api/config/config_entries/flow'
    payload = {
        "handler": "broadlink",
        "show_advanced_options": True
    }
    res = requests.post(url_flow, data=json.dumps(payload), headers=headers)
    if res.status_code == 200:
        data = res.json()
        payload_2 = {
            "host": ip,
            "timeout": timeout
        }
        # print(data['flow_id'])
        url_flow_id = url_flow + '/' + data['flow_id']
        res_flow_id = requests.post(
            url_flow_id, data=json.dumps(payload_2), headers=headers)
        # print(res_flow_id.json())
        if res_flow_id.status_code == 200:
            payload_2 = {
                "name": name_devices
            }
            result = requests.post(
                url_flow_id, data=json.dumps(payload_2), headers=headers)
            result = result.json()
        else:
            result = 'Can not find any devices'
    else:
        result = 'Failed to connect'
    return jsonify(result=result)


@mod.route('/delete_broadlink', methods=['GET', 'POST', 'DELETE'])
def delete_broadlink():
    title = request.args.get('title')
    secrets = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    token = secrets['token']
    headers = {
        "Authorization": "Bearer " + token,
        'Content-Type': 'application/json'
    }
    url = 'http://'+local_ip+':8123/api/config/config_entries/entry'
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        list_broadlink = [i for i in res.json() if i['domain'] == 'broadlink']

    for i in list_broadlink:
        if i['title'] == title:
            url = url + '/' + i['entry_id']
            res = requests.delete(url, headers=headers)
    return show_broadlink_switch()


@mod.route('/add_switch_sensor', methods=['GET', 'POST'])
def add_switch_sensor():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            secrets_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            data = yaml2dict(secrets_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            # try:
            res_entity = requests.get(
                URL_STATE, headers=headers)
            list_entity = res_entity.json()
            entitys = []
            for en in list_entity:
                # print(en)
                if "friendly_name" in en["attributes"].keys():
                    if en['entity_id'].find('sensor') != -1:
                        entitys.append(
                            en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
            # except:
                # entitys = {}
            # print(entitys)
            if request.method == 'GET':
                secrets_file = os.path.join(ROOT_DIR, 'secrets.yaml')
                data = yaml2dict(secrets_file)
                authen_code = data['token']
                headers = {
                    "Authorization": "Bearer " + authen_code,
                    "content-type": "application/json"
                }
                # try:
                res_entity = requests.get(
                    URL_STATE, headers=headers)
                list_entity = res_entity.json()
                entitys = []
                for en in list_entity:
                    # print(en)
                    if "friendly_name" in en["attributes"].keys():
                        if en['entity_id'].find('sensor') != -1:
                            entitys.append(
                                en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
                # except:
                    # entitys = {}
                entitys.sort()
                return render_template('./switch_mqtt/switch_sensor.html', list_entitys=entitys, info='')
            if request.method == "POST":
                filename = os.path.join(ROOT_DIR, 'switch.yaml')
                mqtt_data = yaml2dict(filename)

                entity = request.form['entity'].split(
                    '(')[1].replace(')', '').strip().split('.')[1]
                name = request.form['name']
                payload_off = request.form["payload_off"]
                payload_on = request.form["payload_on"]
                info = ""
                entity = entity.split('_')[0]
                for data in mqtt_data:
                    if data['platform'] == 'mqtt':
                        # print(data['command_topic'])
                        if data['command_topic'].find(entity) != -1:
                            info = "Thiết bị đã tồn tại"
                # print('==================', entity)

                adding_data = {
                    "platform": "mqtt",
                    "ip": "unknown",
                    "netid": entity,
                    "n_switch": "unknown"
                }
                mqtt_reference_file = os.path.join(ROOT_DIR, 'mqtt.yaml')
                mqtt_reference_data = yaml2dict(mqtt_reference_file)
                mqtt_reference_data.append(adding_data)
                # print(mqtt_reference_data)
                dict2yaml(mqtt_reference_data, mqtt_reference_file)
                mqtt_data.append(
                    {
                        "platform": "mqtt",
                        "command_topic": 'zigbee2mqtt/'+entity+'/set',
                        "name": name,
                        "payload_off": payload_off,
                        "payload_on": payload_on,
                        "state_topic": 'zigbee2mqtt/'+entity+'/state'
                    }
                )
                if info == "":
                    dict2yaml(mqtt_data, filename)
                else:
                    return render_template('./switch_mqtt/switch_sensor.html', list_entitys=entitys, info=info)
                return show_mqtt()
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/mqtt')
def show_mqtt():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            mqtt_file = os.path.join(ROOT_DIR, 'mqtt.yaml')
            check_exist(mqtt_file)
            list_mqtt = yaml2dict(mqtt_file)
            return render_template('./switch_mqtt/switch_mqtt.html', list_mqtt=list_mqtt, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')

# quan ly rem dooya


@mod.route('/dooya_cover')
def show_dooya_cover():
    if 'logged_in' in session:
        if session['logged_in']:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            list_dooya = yaml2dict(os.path.join(ROOT_DIR, 'dooya_cover.yaml'))
            return render_template('./dooya_cover/dooya_cover.html', list_dooya=list_dooya, info=info)
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_dooya_cover')
def add_dooya_cover():
    if 'logged_in' in session:
        if session['logged_in']:
            return render_template('./dooya_cover/add_dooya_cover.html')
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_dooya_cover', methods=['POST'])
def add_dooya_cover_handle():
    filename = os.path.join(ROOT_DIR, 'dooya_cover.yaml')
    list_dooya = yaml2dict(filename)
    data = {
        "platform": "dooya_cover",
        "ip_address": request.form['ip'],
        "mac": request.form['mac'],
        "friendly_name": request.form['name']
    }
    list_dooya.append(data)
    dict2yaml(list_dooya, filename)
    return show_dooya_cover()


@mod.route('/econtrol_broadlink', methods=['GET', 'POST'])
def econtrol_broadlink():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            is_connect_with_old_wifi()
            # wifi networks available to connect:
            wifi_list, signal_list, security_list = get_wifi_list()
            # wifi network is still connecting:
            command = 'nmcli -f GENERAL.CONNECTION dev show wlan0'
            broadlink_step1 = 'Bước 1: Kết nối bộ HC vào mạng của Broadlink'
            try:
                wifi_connected = os.popen(command).read().split(
                    'GENERAL.CONNECTION: ')[1].strip()
                known_wifi_list = know_wifi_list()
                try:
                    connected_to_ip = get_ip_from_wifi_connected()
                except:
                    connected_to_ip = ''
                return render_template('./wifi/wifi.html', wifi_list=wifi_list, signal_list=signal_list, security_list=security_list, wifi_connected=wifi_connected, known_wifi_list=known_wifi_list, connected_to_ip=connected_to_ip, broadlink_step1=broadlink_step1)
            except Exception as err:
                error = "Thiết bị này không hỗ trợ mạng WIFI"
                return render_template('./index.html', error=error)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/check_available', methods=['GET', 'POST'])
def check_available():
    set_eth0_default()
    devices = broadlink.discover(timeout=5)
    info = str(devices).split("|")
    list_ip = [i.split("at ")[1].split(":")[0]
               for i in info if(i.find("at ") != -1)]
    list_broadlink, list_mac, list_host = broadlink_devices_info()
    list_ip = [i for i in list_ip if (i not in list_host)]
    return jsonify(list_ip=list_ip)


@mod.route('/check_connect', methods=['GET', 'POST'])
def check_connect():
    # check is_wlan0
    if (is_wifi_support()):
        # check is_eth0
        if (is_eth0()):
            ip = get_ip_from_eth0()
            return jsonify(result="eth0=OK", eth0=ip)
        else:
            return jsonify(result="eth0=none")
    else:
        return jsonify(result="wlan0=none")
