from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
import threading
from utils import *
import websocket
from no_accent_vietnamese import no_accent_vietnamese
mod = Blueprint('air_conndition', __name__)

# thao tac voi thiet bi climate


@mod.route('/climate')
def show_climate():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            climate_file = os.path.join(ROOT_DIR, 'climate.yaml')
            # climate_mqtt_file = os.path.join(ROOT_DIR, 'climate_mqtt.yaml')
            check_exist(climate_file)
            list_climate = yaml2dict(climate_file)
            # list_climate_mqtt = yaml2dict(climate_mqtt_file)
            # print(list_climate_mqtt)
            # return render_template('./air_condition/climate.html', list_climate=list_climate, list_climate_mqtt=list_climate_mqtt, info=info)
            return render_template('./air_condition/climate.html', list_climate=list_climate, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_climate')
def add_climate_device():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            list_broadlink = get_broadlink_device_from_api()
            IR_CODE = load_ircode()
            list_ir = IR_CODE['climate']
            list_ir = {k: v for k, v in sorted(list_ir.items())}
            
            list_javis_ir = get_javis_dev()
            return render_template('./air_condition/add_climate.html', list_gateway=list_broadlink, list_ir=list_ir, list_javis_ir=list_javis_ir)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_climate', methods=['POST'])
def add_climate_result():
    if request.method == 'POST':
        # print(request.form)
        filename = os.path.join(ROOT_DIR, 'climate.yaml')
        data = dict()
        data['name'] = request.form['name']
        data['controller_data'] = request.form['entity_id']
        data['unique_id'] = no_accent_vietnamese(
            request.form["name"]).lower().replace(" ", "_") + str(int(time.time()))
        device_code = int(request.form["device_code"].split("(")[-1][:-1])
        data['device_code'] = device_code
        data['platform'] = 'smartir'
        check_exist(filename)
        dict_ = yaml2dict(filename)
        dict_.append(data)
        dict2yaml(dict_, filename)
        return show_climate()


@mod.route('/delete_climate', methods=['POST'])
def del_climate():
    name = request.args.get('name')
    list_TV = yaml2dict(os.path.join(ROOT_DIR, 'climate.yaml'))
    list_TV = [i for i in list_TV if i['name'] != name]
    dict2yaml(list_TV, os.path.join(ROOT_DIR, 'climate.yaml'))
    return show_climate()


@mod.route('/test_climate', methods=['POST'])
def test_climate():
    device = request.args.get('device')
    mod = device + '.json'
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/climate/', mod)
    # print('dir: ', filedir)

    with open(filedir) as json_file:
        data = json.load(json_file)
        operationModes = data['operationModes']
        fanModes = data['fanModes']
        # print(operationModes, fanModes)
    return jsonify(operationModes=operationModes, fanModes=fanModes)


@mod.route('/check_command_climate_off', methods=['POST'])
def climate_off():
    entity_id = request.args.get('gateway')
    device = request.args.get('model')
    mac, host = from_entity_id_get_mac_ip(entity_id)
    model = device + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/climate/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        off_cmd = data['commands']['off']
        sending_ir_packet(mac, host, off_cmd)
    return jsonify()


@mod.route('/check_command_climate_on', methods=['POST'])
def climate_on():
    entity_id = request.args.get('gateway')
    device = request.args.get('model')
    model = device + '.json'
    mac, host = from_entity_id_get_mac_ip(entity_id)

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/climate/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        try:
            climate_on = data['commands']['cool']['auto']['26']
        except:
            climate_on = data['commands']['cool']['high']['26']
        sending_ir_packet(mac, host, climate_on)
    return jsonify()


@mod.route('/check_command_climate', methods=['POST'])
def check_command_climate():
    entity_id = request.args.get('gateway')
    model = request.args.get('model')
    order = request.args.get('order')
    mac, host = from_entity_id_get_mac_ip(entity_id)
    model = model + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/climate/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        cool_mode = data['commands']['cool']
        count_loop = 0
        for key in cool_mode:
            if (count_loop == int(order)):
                mod = cool_mode[key]
                for k in mod:
                    cmd = cool_mode[key][k]
                    sending_ir_packet(mac, host, cmd)
                    break
                break
            count_loop += 1
    return jsonify()


@mod.route('/add_climate_mqtt', methods=['GET', 'POST'])
def add_climate_mqtt():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                return render_template('./climate_mqtt/add_climate_mqtt.html', err='')
            else:
                topic = request.form['topic']
                device_name = topic.split("/")[1]
                with open(os.path.join(data_file, 'climate_code.json'), 'r') as json_file:
                    climate_data = json.load(json_file)
                device_data = climate_data['climate'][device_name]
                modes = device_data['mode']
                fan_modes = device_data['fan_mode']
                file_name = os.path.join(ROOT_DIR, 'climate.yaml')
                try:
                    list_climate_mqtt = yaml2dict(file_name)
                except Exception:
                    f = open(file_name, "w")
                    list_climate_mqtt = []
                    f.close()

                list_climate_mqtt.append({
                    "platform": "mqtt",
                    "name": request.form['name'],
                    "min_temp": 18,
                    "max_temp": 30,
                    "modes": modes,
                    "fan_modes": fan_modes,
                    "power_command_topic": topic + "/power/set",
                    "mode_command_topic": topic + "/mode/set",
                    "temperature_command_topic": topic + "/temperature/set",
                    "fan_mode_command_topic": topic + "/fan/set",
                    "swing_mode_command_topic": topic + "/swing/set",
                    "mode_state_topic": topic + "/mode/state",
                    "temperature_state_topic": topic + "/temperature/state",
                    "fan_mode_state_topic": topic + "/fan/state",
                    "swing_mode_state_topic": topic + "/swing/state",
                    "precision": 1.0
                })
                dict2yaml(list_climate_mqtt, file_name)
                return show_climate()


@mod.route('/connect_mqtt', methods=['POST'])
def connect_mqtt():
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    string_web = "ws://"+local_ip+":8123/api/websocket"
    ws = websocket.create_connection(string_web)
    result = ws.recv()
    payload = {
        "type": "auth",
        "access_token": secret_data['token']
    }
    ws.send(json.dumps(payload))
    result = ws.recv()
    if (json.loads(result)['type'] == 'auth_invalid'):
        return jsonify(data=result)
    else:
        payload = ({
            "id": 22,
            "topic": "#",
            "type": "mqtt/subscribe"
        })
        ws.send(json.dumps(payload))
        result = ws.recv()
        while(1):
            result = ws.recv()
            if (json.loads(result)['type'] == 'event'):
                topic = json.loads(result)['event']['topic']
                if (topic.find('mode') != -1):
                    topic = topic.split('/mode/state')[0]
                    break
        return jsonify(topic=topic)
