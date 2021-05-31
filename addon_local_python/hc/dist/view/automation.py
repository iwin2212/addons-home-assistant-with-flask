import os
from yaml_util import yaml2dict, dict2yaml
from const import ROOT_DIR
import yaml
from flask import Flask, render_template, request, redirect, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import re
import uuid
import time
mod = Blueprint('automation', __name__)


@mod.route('/automation')
def show_automation():
    if 'logged_in' in session:
        if session['logged_in']:
            filename = os.path.join(ROOT_DIR, 'automations.yaml')
            check_exist(filename)
            list_automation = yaml2dict(filename)
            list_automation = [i for i in list_automation if (i.get('alias') != 'armed_away') and (
                i.get('alias') != 'armed_home') and (i.get('alias') != 'disarmed') and (i.get('alias') != 'triggered')]
            list_entity_id = []
            for i in list_automation:
                list_entity_id.append('automation.' + ''.join(e for e in no_accent_vietnamese(
                    i['alias']).lower().replace(" ", "_") if e.isalnum() or e == "_"))
            # print(list_automation)
            return render_template('./automation/automations.html', list_automation=list_automation, list_entity_id=list_entity_id)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/enable_automation', methods=['POST'])
def enable_automation():
    entity_id = request.args.get('entity_id')
    URL = "http://localhost:8123/api/services/automation/{}"
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }

    dat = str({"entity_id": entity_id}).replace("\'", "\"").encode()
    try:
        if request.form["enable"] == "YES":
            action = "turn_on"
            requests.post(URL.format(action), data=dat, headers=headers)
        else:
            action = "turn_off"
            requests.post(URL.format(action), data=dat, headers=headers)
    except:
        action = "turn_off"
        requests.post(URL.format(action), data=dat, headers=headers)
    return redirect('./automation')


@mod.route('/delete_automation', methods=["POST"])
def delete_automation():
    iden = request.args.get('automation_id')
    list_automation = yaml2dict(os.path.join(ROOT_DIR, 'automations.yaml'))
    # print('------------------\n', iden, '\n------------------\n')
    if iden.find('app_syncState_') != -1 or iden.find('app_bathRoom_') != -1 or iden.find('app_timer_') != -1:
        if (iden.endswith('_1')):
            name = iden[0:len(iden)-2]
            new_list = [i for i in list_automation if i['id'].find(name) == -1]
        else:
            new_list = [i for i in list_automation if i['id'].find(iden) == -1]
    else:
        new_list = [i for i in list_automation if 'id' in i if i['id'] != iden]
    dict2yaml(new_list, os.path.join(ROOT_DIR, 'automations.yaml'))
    # restart automation luon
    restart_automation()
    return show_automation()


@mod.route('/add_automation_dongbo')
def add_automation_interface():
    if 'logged_in' in session:
        if session['logged_in']:
            list_devices = get_devices()
            list_entity_id = []
            list_entity_name = []
            for i in list_devices:
                list_entity_id.append(i['entity_id'])
                try:
                    if(i['attributes'].get('device_class') == 'tv'):
                        list_entity_name.append(
                            'TV: ' + i['attributes']['friendly_name'])
                    else:
                        list_entity_name.append(
                            i['attributes']['friendly_name'])
                except:
                    list_entity_name.append('Thiết bị không có tên')
            return render_template('./automation/add_automation_dongbo.html', list_entity_id=list_entity_id, list_entity_name=list_entity_name)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route("/new_automation", methods=['GET', 'POST'])
def new_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = []
                list_entity_name = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                list_services = get_services()
                result_service = {}
                result_list_service = []
                for ser in list_services:
                    for en in list_entity_id:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                file_dir = os.path.join(
                    ROOT_DIR, '.storage', 'core.restore_state')
                for i in result_service:
                    for j in result_service[i]:
                        result_list_service.append(i+"."+j)
                result_list_service.sort()
                return render_template('./automation/new_automation.html', list_entity_name=list_entity_name,
                                       list_entity_id=list_entity_id, list_services=result_list_service)
            elif request.method == 'POST':
                # print('#################\n POST\n###############\n')
                # print('-----------------\n request.form\n-----------------\n',
                #       request.form, '\n-----------------')
                data = {}
                data['id'] = str(int(time.time()))
                data['alias'] = request.form['ten']
                typescript = request.form['type']
                data['trigger'] = deal_with_trigger()
                data['condition'] = deal_with_condition()
                data['action'] = deal_with_action()

                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                automation.append(data)
                dict2yaml(automation, filename)

                # restart automation luon
                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


# all timer
@mod.route('/add_timer', methods=['GET', 'POST'])
def add_timer():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == "GET":
                list_entity_id = []
                list_devices = get_devices()
                list_entity_name = []
                for i in list_devices:
                    if i['entity_id'].split(".")[0] in ['switch', 'light', 'media_player', 'climate', 'automation', 'fan']:
                        list_entity_id.append(i['entity_id'])
                        try:
                            if(i['attributes'].get('device_class') == 'tv'):
                                list_entity_name.append(
                                    'TV: ' + i['attributes']['friendly_name'])
                            else:
                                list_entity_name.append(
                                    i['attributes']['friendly_name'])
                        except:
                            list_entity_name.append('Thiết bị không có tên')
                list_services = get_services()

                result_service = {}
                result_list_service = []
                for ser in list_services:
                    for en in list_entity_id:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                            # print(en)

                # print(list_devices)
                # error services
                for i in result_service:
                    for j in result_service[i]:
                        result_list_service.append(i+"."+j)
                # print(result_list_service)
                result_list_service.sort()
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                # print(list_entity_id)
                # print(list_entity_name)
                list_entities = []
                loop = 0
                for i in list_entity_name:
                    loop += 1
                    list_entities.append(
                        i + ' (' + list_entity_id[loop-1] + ')')
                # print(list_entities)
                return render_template('./automation/add_timer.html', list_entities=list_entities, list_entity_id=list_entity_id, list_entity_name=list_entity_name, list_services=result_list_service)
            elif request.method == "POST":
                # print('-------------', request.form)
                entity_id = request.form['entity'].split('(')[1].split(')')[0]
                service = request.form["action"]
                if service == 'climate.set_temperature':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "hvac_mode": request.form['mode'],
                            "temperature": request.form['temperature']
                        },
                        "service": service
                    }]
                elif service == 'climate.set_fan_mode':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "fan_mode": request.form['fan_mode']
                        },
                        "service": service
                    }]
                elif service == 'cover.set_cover_position':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "position": request.form['pct_open']
                        },
                        "service": service
                    }]
                elif service == 'light.turn_on':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "color_name": request.form['color']
                        },
                        "service": service
                    }]
                elif service == 'media_player.volume_set':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "volume_level": (int(request.form['volume'])/100)
                        },
                        "service": service
                    }]
                elif service == 'media_player.select_source':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "source": request.form['source']
                        },
                        "service": service
                    }]
                elif service == 'media_player.speak':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "message": request.form['message']
                        },
                        "service": 'tts.google_translate_say'
                    }]
                elif service.split('.')[0] == 'alarm_control_panel':
                    action_data = [{
                        "data": {
                            "entity_id": entity_id,
                            "code": int(request.form['alarm_code'])
                        },
                        "service": service
                    }]
                else:
                    action_data = [{
                        "data": {
                            "entity_id": entity_id
                        },
                        "service": service
                    }]

                day_in_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                list_day = []
                for i in day_in_week:
                    try:
                        request.form[i]
                        list_day.append(i)
                    except:
                        pass
                        # print("Cannot get", i)
                data = {
                    "action": action_data,
                    "alias": request.form["ten"],
                    "condition": [{
                        "condition": "time",
                        "weekday": list_day
                    }] if list_day != [] else [],
                    "id": "app_timer_" + str(int(time.time())),
                    "trigger": [
                        {
                            "at": request.form["time"],
                            "platform": "time"
                        }
                    ]
                }

                list_automation = yaml2dict(
                    os.path.join(ROOT_DIR, 'automations.yaml'))
                list_automation.append(data)
                dict2yaml(list_automation, os.path.join(
                    ROOT_DIR, 'automations.yaml'))
                list_entity_id = []
                list_devices = get_devices()
                list_services = get_services()
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])

                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html', err='')
    else:
        return render_template('./login.html', err='')


@mod.route('/add_tts_nhaclich', methods=['GET', 'POST'])
def add_tts_nhaclich():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                list_entity_id = []
                list_entity_name = []
                list_devices = get_devices()
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                if list_entity_id == []:
                    return "Không có thiết bị phát âm thanh nào, vui lòng cấu hình thiết bị và thử lại"
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name)))
                return render_template('./automation/add_tts_nhaclich.html', list_entity_id=list_entity_id,
                                       list_entity_name=list_entity_name)
            else:
                day_in_week = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                list_day = []
                for i in day_in_week:
                    try:
                        if (request.form[i] != 0):
                            list_day.append(i)
                    except:
                        pass
                try:
                    data = {
                        "action": [{
                            "service": "tts.google_translate_say",
                            "data": {
                                "message": request.form["msg"],
                                "entity_id": request.form["entity_id"].split("(")[-1][:-1]
                            }
                        }],
                        "alias": request.form["ten"],
                        "condition": [{
                            "condition": "time",
                            "weekday": list_day
                        },
                            {
                            "condition": "state",
                            "entity_id": request.form["door_sensor"].split("(")[-1][:-1],
                            "state": request.form["state"]
                        }] if list_day != [] else [],
                        "id": "tts_nhaclich." + str(uuid.uuid4()).replace("-", ""),
                        "trigger": [
                            {
                                "at": request.form["time"],
                                "platform": "time"
                            }
                        ]
                    }
                except:
                    data = {
                        "action": [{
                            "service": "tts.google_translate_say",
                            "data": {
                                "message": request.form["msg"],
                                "entity_id": request.form["entity_id"].split("(")[-1][:-1]
                            }
                        }],
                        "alias": request.form["ten"],
                        "condition": [{
                            "condition": "time",
                            "weekday": list_day
                        }] if list_day != [] else [],
                        "id": "tts_nhaclich." + str(uuid.uuid4()).replace("-", ""),
                        "trigger": [
                            {
                                "at": request.form["time"],
                                "platform": "time"
                            }
                        ]
                    }
                list_automation = yaml2dict(
                    os.path.join(ROOT_DIR, 'automations.yaml'))
                list_automation.append(data)
                dict2yaml(list_automation, os.path.join(
                    ROOT_DIR, 'automations.yaml'))
                list_entity_id = []
                list_devices = get_devices()
                list_services = get_services()
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])

                restart_automation()
                return show_automation()


@mod.route('/add_bathroom_automation', methods=['GET', 'POST'])
def add_bathroom_automation():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                list_entity_id = []
                list_entity_name = []
                list_devices = get_devices()
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name)))
                list_services = get_services()
                return render_template('./automation/add_bathroom_automation.html', list_entity_id=list_entity_id, list_services=list_services,
                                       list_entity_name=list_entity_name)
            else:
                code = str(int(time.time()))
                name = request.form["ten"]
                after = str(request.form["after"])
                before = str(request.form["before"])
                if after == "":
                    if before != "":
                        effective_time_condition = [{
                            "condition": "time",
                            "before": before
                        }]
                else:
                    if before == "":
                        effective_time_condition = [{
                            "condition": "time",
                            "after": after
                        }]
                    else:
                        effective_time_condition = [{
                            "condition": "time",
                            "after": after,
                            "before": before
                        }]
                try:
                    motion = request.form['motion'].split("(")[1][:-1]
                except:
                    motion = None
                try:
                    door = request.form['door'].split("(")[1][:-1]
                except:
                    door = None
                # input_bool = request.form['input_boolean'].split("(")[1][:-1]

                switch = request.form.getlist('switch')
                # print(switch)
                switch_condition_on = [{
                    'condition': 'state',
                    "entity_id": switch[0].split("(")[1][:-1],
                    "state": "on"
                }]
                switch_condition_off = [{
                    'condition': 'state',
                    "entity_id": switch[0].split("(")[1][:-1],
                    "state": "off"
                }]
                action_on = []
                for i in switch:
                    entity_id = i.split("(")[1][:-1]
                    action_on.append({
                        "service": entity_id.split(".")[0] + ".turn_on",
                        "data": {
                            "entity_id": entity_id
                        }
                    })
                action_off = []
                for i in switch:
                    entity_id = i.split("(")[1][:-1]
                    action_off.append({
                        "service": entity_id.split(".")[0] + ".turn_off",
                        "data": {
                            "entity_id": entity_id
                        }
                    })
                # kịch bản 1 ###################################################
                if (request.form['bathroom_type'] == 'Loại 2 ngăn: ngăn vệ sinh và ngăn tắm riêng (1 cảm biến cửa và 1 cảm biến chuyển động)'):
                    mocua_batden = {  # khi mở cửa mà đèn đang tắt bật nó lên
                        "alias": name + code + "1",
                        "id": "app_bathRoom_" + code + "_1",
                        "trigger": [{
                            "platform": "state",
                            "to": "on",
                            "entity_id": door
                        }],
                        "condition": effective_time_condition + switch_condition_off,
                        "action": action_on
                    }
                else:
                    mocua_batden = {  # khi mở cửa mà đèn đang tắt bật nó lên
                        "alias": name + code + "1",
                        "id": "app_bathRoom_" + code + "_1",
                        "trigger": [{
                            "platform": "state",
                            "to": "on",
                            "entity_id": door
                        }],
                        "condition": effective_time_condition + switch_condition_off,
                        "action": action_on + [{"data": {"entity_id": "automation." + name.replace(" ", "_") + code + "6"}, "service": "automation.turn_on"}, {"data": {"entity_id": "automation." + name.replace(" ", "_") + code + "7"}, "service": "automation.turn_on"}]
                    }
                # kịch bản 2 ###################################################
                mocua_tatden = {  # khi mở cửa mà đèn đang bật thì tắt nó đi
                    "alias": name + code + "2",
                    "id": "app_bathRoom_" + code + "_2",
                    "trigger": [{
                        "platform": "state",
                        "to": "on",
                        "entity_id": door
                    }],
                    "condition": effective_time_condition + switch_condition_on + [{
                        "condition": "state",
                        "state": "on",
                        "entity_id": motion
                    }] if motion != None else effective_time_condition + switch_condition_on,
                    "action": action_off
                }
                list_automation = yaml2dict(
                    os.path.join(ROOT_DIR, 'automations.yaml'))
                list_automation.append(mocua_batden)
                # list_automation.append(mocua_inputbool)
                if door != None:
                    # kịch bản 3 ###################################################
                    chuyendong_tatden = {  # khi khong co chuyen dong ma dang bat den, mo cua thi tat
                        "alias": name + code + "3",
                        "id": "app_bathRoom_" + code + "_3",
                        "trigger": [{
                            "platform": "state",
                            "to": "off",
                            "entity_id": motion,
                                    "for": "00:" + request.form["time_motion"]
                                    }],
                        "condition": effective_time_condition + [{
                            "condition": "state",
                            "state": "on",
                            "entity_id": door
                        }] + switch_condition_on,
                        "action": action_off
                    }
                # kịch bản 4 ###################################################
                    chuyendong_batden = {
                        "alias": name + code + "4",
                        "id": "app_bathRoom_" + code + "_4",
                        "trigger": [{
                            "platform": "state",
                            "to": "on",
                            "entity_id": motion,
                                    "for": "00:00:00",
                                    }],
                        "condition": effective_time_condition + switch_condition_off,
                        "action": action_on
                    }
                # kịch bản 5 ###################################################
                # nếu đèn bật 30ph mà không có chuyển động thì tắt đèn
                nomotion_turnoff = {
                    "alias": name + code + "5",
                    "id": "app_bathRoom_" + code + "_5",
                    "trigger": [{
                        "platform": "state",
                        "to": "off",
                        "entity_id": motion,
                                "for": "00:30:00"
                                }],
                    "condition": effective_time_condition + [{
                        "condition": "state",
                        "state": "off",
                        "entity_id": motion
                    }, {
                        "condition": "state",
                        "state": "off",
                        "entity_id": door
                    }] + switch_condition_on,
                    "action": action_off
                }
                if (request.form['bathroom_type'] == 'Loại 2 ngăn: ngăn vệ sinh và ngăn tắm riêng (1 cảm biến cửa và 1 cảm biến chuyển động)'):
                    with open("data_file.json", "w") as write_file:
                        json.dump([chuyendong_tatden, chuyendong_batden,
                                   nomotion_turnoff, mocua_tatden], write_file)
                else:
                    # kịch bản 6 ###################################################
                    # đóng cửa sau 3 phút không phát hiện chuyển động thì tắt đèn
                    nomotion_turnoff_instant = {
                        "alias": name + code + "6",
                        "id": "app_bathRoom_" + code + "_6",
                        "trigger": [{
                            "platform": "state",
                            "to": "off",
                            "entity_id": motion,
                            "for": "00:02:00"
                        }],
                        "condition": effective_time_condition + [{
                            "condition": "state",
                            "state": "off",
                            "entity_id": door
                        }] + switch_condition_on,
                        "action": action_off + [{"data": {"entity_id": "automation." + name.replace(" ", "_") + code + "7"}, "service": "automation.turn_off"}]
                    }
                    # kịch bản 7 ###################################################
                    if (request.form['bathroom_type'] == 'Loại 2 ngăn: ngăn vệ sinh và ngăn tắm riêng (1 cảm biến cửa và 2 cảm biến chuyển động)'):
                        turnoff_automation6 = {
                            "alias": name + code + "7",
                            "id": "app_bathRoom_" + code + "_7",
                            "trigger": [{
                                "platform": "state",
                                "from": "off",
                                "to": "on",
                                "entity_id": motion
                            }, {
                                "platform": "state",
                                "from": "off",
                                "to": "on",
                                "entity_id": request.form['motion_2'].split('(')[1].split(')')[0]
                            }],
                            "condition": effective_time_condition + [{
                                "condition": "state",
                                "state": "off",
                                "entity_id": door
                            }] + switch_condition_on,
                            "action": [{"data": {"entity_id": "automation." + name.replace(" ", "_") + code + "6"}, "service": "automation.turn_off"}]
                        }
                    else:
                        turnoff_automation6 = {
                            "alias": name + code + "7",
                            "id": "app_bathRoom_" + code + "_7",
                            "trigger": [{
                                "platform": "state",
                                "from": "off",
                                "to": "on",
                                "entity_id": motion
                            }],
                            "condition": effective_time_condition + [{
                                "condition": "state",
                                "state": "off",
                                "entity_id": door
                            }] + switch_condition_on,
                            "action": [{"data": {"entity_id": "automation." + name.replace(" ", "_") + code + "6"}, "service": "automation.turn_off"}]
                        }
                    with open("data_file.json", "w") as write_file:
                        json.dump([chuyendong_tatden, chuyendong_batden, nomotion_turnoff,
                                   mocua_tatden, nomotion_turnoff_instant, turnoff_automation6], write_file)

                f = open('data_file.json', 'r')
                dat = json.load(f)
                list_automation.extend(dat)
                dict2yaml(list_automation, os.path.join(
                    ROOT_DIR, 'automations.yaml'))
                list_entity_id = []
                list_devices = get_devices()
                list_services = get_services()
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])

                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


def find_timestamp(iden):
    i = len(iden) - 1
    string = ''
    while iden[i].isdigit():
        string = iden[i] + string
        i -= 1
    return string


def find_integer(string):
    integer = ''
    i = len(string) - 1
    while string[i].isdigit():
        integer = string[i] + integer
        i -= 1
    return integer


def find_minute(template):
    template_spl = template.split("*")
    return find_integer(template_spl[0])


def parse_action(data):
    list_action = []
    # print(data)
    for i in range(len(data)):
        # print('-------------------\n', data[i], '\n--------------')
        if 'delay' in data[i]:
            list_action.append({
                'delay': data[i]['delay']
            })
        if 'service' in data[i]:
            list_action.append(data[i])
    # print(list_action)
    return list_action


def parse_condition(data):
    list_condition = []
    for i in range(len(data)):

        if data[i]['condition'] == 'state':
            # print("{:30}{:>30}".format("Entity ID", data[i]['entity_id']))
            # print("{:30}{:>30}".format("State", data[i]['state']))
            list_condition.append({
                "condition": "state",
                "state": "On" if data[i]["state"] != 'off' else 'Off',
                "entity_id": data[i]['entity_id']
            })
        elif data[i]['condition'] == 'numeric_state':
            # print("{:30}{:>30}".format("Entity ID", data[i]['entity_id']))
            dat = {"condition": "numeric_state",
                   "entity_id": data[i]["entity_id"]}
            try:
                # print("{:30}{:>30}".format("Above", data[i]['above']))
                dat['above'] = data[i]['above']
            except:
                pass
            try:
                # print("{:30}{:>30}".format("Below", data[i]['below']))
                dat['below'] = data[i]['below']
            except:
                pass
            list_condition.append(dat)
        elif data[i]['condition'] == 'time':
            dat = {"condition": "time"}
            # print("{:30}{:>30}".format(
            # "Time", data[i]["after"] + "to" + data[i]["before"]))
            try:
                # print("{:30}{:>30}".format("After", data[i]['after']))
                dat['after'] = data[i]['after']
            except:
                pass
            try:
                # print("{:30}{:>30}".format("Before", data[i]['before']))
                dat['before'] = data[i]['before']
            except:
                pass
            list_condition.append(dat)
    return list_condition


def parse_trigger(data):
    list_trigger = []
    for i in range(len(data)):
        if data[i]['platform'] == 'state':
            dat = {"platform": "state"}
            # print("{:30}{:>30}".format("entity id", data[i]['entity_id']))
            dat["entity_id"] = data[i]["entity_id"]
            # print("{:30}{:>30}".format("To state", data[i]['to']))
            try:
                dat["to"] = data[i]['to']
            except:
                pass
            try:
                # print("{:30}{:>30}".format("From state", data[i]['from']))
                dat["from"] = data[i]['from']
                # print('-------o0o--------', dat["from"])
            except:
                pass
            try:
                # print("{:30}{:>30}".format("For", data[i]['for']))
                dat["for"] = data[i]["for"]
            except:
                pass
        elif data[i]['platform'] == 'numeric_state':
            dat = {"platform": "numeric_state"}
            dat["entity_id"] = data[i]["entity_id"]
            try:
                # print("{:30}{:>30}".format("Above", data[i]["above"]))
                dat["above"] = data[i]["above"]
            except:
                pass
            try:
                # print("{:30}{:>30}".format("Below", data[i]['below']))
                dat["below"] = data[i]["below"]
            except:
                pass
            try:
                # print("{:30}{:>30}".format("For", data[i]['for']))
                dat["for"] = data[i]["for"]
            except:
                pass
        elif data[i]["platform"] == "time":
            dat = data[i]
        list_trigger.append(dat)
    return list_trigger


def parse_automation_tongquat(data):
    list_action = data['action']
    # print(data['action'])
    list_trigger = data['trigger']
    try:
        list_condition = data['condition']
    except:
        list_condition = []
    name = data['alias']
    au_id = data['id']
    # print("************** Parse Trigger *****************")
    list_trigger = parse_trigger(list_trigger)
    # print("************** Parse Condition *****************")
    list_condition = parse_condition(list_condition)
    # print("************** Parse Action *****************")
    list_action = parse_action(list_action)
    return list_trigger, list_condition, list_action


def parse_dongbo_automation(data):
    list_automation = yaml2dict(os.path.join(ROOT_DIR, 'automations.yaml'))
    name = data["alias"].replace(" chiều đi", "").replace(" chiều về", "")
    # print("{:35}{:>35}".format("Tên", name))
    count = 0
    for i in list_automation:
        if i['alias'].find(name) != -1:
            count += 1
    entity1 = data['trigger']['entity_id']
    entity2 = data['action']['entity_id']
    # if count == 2:
    #     print("{:35}{:>35}".format("Kiểu đồng bộ", "2 chiều"))
    # else:
    #     print("{:35}{:>35}".format("Kiểu đồng bộ", "1 chiều"))
    # print("{:35}{:>35}".format("Thiết bị 1", entity1))
    # print("{:35}{:>35}".format("Thiết bị 2", entity2))
    return count, entity1, entity2


def parse_timer(data):
    # phai tim duoc khoang thoi gian, condition la list ngay, action la cac tham so
    name = data["alias"]
    trigger = data["trigger"][0]
    condition = data["condition"][0]["weekday"] if data["condition"] != [] else [
        "mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    list_action = data["action"]
    return name, trigger, condition, list_action


def parse_tts_nhaclich(data):
    name = data["alias"]
    trigger = data["trigger"][0]
    condition = data["condition"]
    action = data["action"][0]
    return name, trigger, condition, action


def automation_info(data):
    if data['id'].find("app_syncState_") != -1:
        return parse_dongbo_automation(data)
    elif data['id'].find('app_timer_') != -1:
        return parse_timer(data)
    elif data['id'].find('tts_nhaclich') != -1:
        return parse_tts_nhaclich(data)
    else:
        return parse_automation_tongquat(data)


@mod.route('/edit_automation', methods=['GET', 'POST'])
def edit_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                iden = request.args.get('iden')
                # print('Iden =', iden)
                automation_file = os.path.join(ROOT_DIR, "automations.yaml")
                list_automation = yaml2dict(automation_file)
                # print(list_automation)
                for i in list_automation:
                    if 'id' in i:
                        if i['id'] == iden:
                            data = i
                            name = i['alias']
                            break
                # print(name)
                automation_data = automation_info(data)
                # print('#############\n', automation_data, '\n#############')
                list_devices = get_devices()
                list_services = get_services()
                list_entity_id = [i['entity_id'] for i in list_devices]
                # print('---------------------------------------',len(list_entity_id))
                list_entity_name = []
                for i in list_devices:
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                result_entity = []
                result_service = {}
                result_list_service = []
                for ser in list_services:
                    for en in list_entity_id:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                            # print(en)
                            if en not in result_entity:
                                result_entity.append(en)
                # print(list_devices)
                # error services
                for i in result_service:
                    for j in result_service[i]:
                        result_list_service.append(i+"."+j)
                # print(result_list_service)
                if iden.find("app_syncState_") != -1:
                    name_entity1 = list_entity_name[[i for i in range(
                        len(list_entity_id)) if list_entity_id[i] == automation_data[1]][0]]
                    name_entity2 = list_entity_name[[i for i in range(
                        len(list_entity_id)) if list_entity_id[i] == automation_data[2]][0]]
                    return render_template('./automation/edit_dongbo_automation.html', automation_data=automation_data, iden=iden, name=name,
                                           list_entity_id=list_entity_id, list_entity_name=list_entity_name,
                                           name_entity1=name_entity1, name_entity2=name_entity2)
                elif iden.find("app_timer_") != -1:
                    name, trigger, condition, action = automation_data
                    # print('automation_data: ', automation_data)
                    # for i in range(len(list_entity_id)):
                    #         print(i)
                    # print([i for i in range(len(list_entity_id)) if list_entity_id[i] == action[0]['data']["entity_id"]])
                    try:
                        action_name = list_entity_name[[i for i in range(
                            len(list_entity_id)) if list_entity_id[i] == action[0]['data']["entity_id"]][0]]
                    except Exception:
                        action_name = "Thiết bị không có tên"
                    action = action[0]

                    list_entities = []
                    for i in range(len(list_entity_id)):
                        list_entities.append(
                            list_entity_name[i] + ' (' + list_entity_id[i] + ')')
                    # print(list_entities)
                    automation_data_schedule = automation_data
                    if (automation_data_schedule[3][0]['data'].get('volume_level') != None):
                        automation_data_schedule[3][0]['data']['volume_level'] = int(
                            automation_data_schedule[3][0]['data']['volume_level']*100)
                    for i in list_entities:
                        if i.split('(')[1].split(')')[0] == automation_data_schedule[3][0]['data']['entity_id']:
                            automation_data_schedule[3][0]['data']['entity_id'] = i
                    return render_template('./edit_schedule.html', automation_data=automation_data_schedule, iden=iden, name=name, trigger=trigger, condition=condition,
                                           list_entity_id=list_entity_id, list_entity_name=list_entity_name, list_entities=list_entities, action=action, list_services=result_list_service)
                elif iden.find("tts_nhaclich") != -1:
                    name, trigger, condition, action = automation_data
                    try:
                        action_name = list_entity_name[[i for i in range(
                            len(list_entity_id)) if list_entity_id[i] == action['data']["entity_id"]][0]]
                    except Exception:
                        action_name = "Thiết bị không có tên"
                    return render_template('./edit_tts_nhaclich.html', automation_data=automation_data, iden=iden, name=name, action=action, trigger=trigger,
                                           list_entity_id=list_entity_id, list_entity_name=list_entity_name, action_name=action_name, condition=condition)
                else:
                    list_trigger_name = []
                    list_condition_name = []
                    list_action_name = []
                    list_trigger = automation_data[0]
                    list_trigger = [
                        i for i in list_trigger if i["platform"] != "time"]
                    time_trigger = None
                    # return str(automation_data)
                    after = ""
                    before = ""
                    delay = ""
                    list_action = []
                    for j in automation_data[0]:
                        if j["platform"] == "time":
                            time_trigger = j
                        else:
                            try:
                                list_trigger_name.append(list_entity_name[[i for i in range(
                                    len(list_entity_id)) if list_entity_id[i] == j["entity_id"]][0]])
                            except Exception:
                                list_trigger_name.append(
                                    "Thiết bị không có tên")
                    list_condition = []
                    for j in automation_data[1]:
                        if j['condition'] != 'time':
                            try:
                                list_condition_name.append(list_entity_name[[i for i in range(
                                    len(list_entity_id)) if list_entity_id[i] == j["entity_id"]][0]])
                            except Exception:
                                list_condition_name.append(
                                    "Thiết bị không có tên")
                            list_condition.append(j)
                        else:
                            try:
                                after = j['after']
                            except:
                                after = ""
                            try:
                                before = j['before']
                            except:
                                before = ""
                    # print('automation_data: ', automation_data)
                    delay = []
                    for j in automation_data[2]:
                        if 'delay' in j:
                            delay.append(j['delay'])
                        else:
                            try:
                                list_action_name.append(list_entity_name[[i for i in range(
                                    len(list_entity_id)) if list_entity_id[i] == j['data']["entity_id"]][0]])
                            except Exception:
                                list_action_name.append(
                                    "Thiết bị không có tên")
                            list_action.append(j)
                    len_dict = len(list_action)
                    count_loop = 0

                    for i in list_action:
                        count_loop += 1
                        i['data']['entity_id'] = list_action_name[count_loop -
                                                                  1] + ' (' + i['data']['entity_id'] + ')'
                        if (i['service'] == 'media_player.volume_set'):
                            i['data']['volume_level'] = int(
                                i['data']['volume_level'] * 100)

                    list_entities = []
                    cnt_loop = 0
                    for i in list_entity_id:
                        cnt_loop += 1
                        list_entities.append(
                            list_entity_name[cnt_loop - 1] + ' (' + list_entity_id[cnt_loop-1] + ')')
                    return render_template('./automation/edit_automation_tongquat.html', list_trigger=list_trigger, list_condition=list_condition,
                                           list_action=list_action, iden=iden, name=name, list_entity_id=list_entity_id, list_entity_name=list_entity_name,
                                           list_trigger_name=list_trigger_name, list_services=result_list_service, list_condition_name=list_condition_name,
                                           list_action_name=list_action_name, after=after, before=before, delay=delay, time_trigger=time_trigger, len_dict=len_dict, list_entities=list_entities)
            else:
                iden = request.args.get('iden')
                if iden.find('app_syncState_') != -1:
                    list_automation = yaml2dict(
                        os.path.join(ROOT_DIR, 'automations.yaml'))
                    kieu = request.form['type']
                    entity1 = request.form["entity1"].split("(")[1][:-1]
                    entity2 = request.form["entity2"].split("(")[1][:-1]
                    # print(entity1, entity2)
                    if kieu.find("một chiều") != -1:
                        data = {
                            "alias": request.form["ten"],
                            "id": "app_syncState_" + str(int(time.time())),
                            "trigger": {
                                "entity_id": entity1,
                                "platform": "state"
                            },
                            "action": {
                                "entity_id": entity2,
                                "service_template": "{% if is_state('" + entity1 + "','on') %} switch.turn_on {% else %} switch.turn_off {% endif %}"
                            }
                        }
                    else:
                        data = [{
                            "alias": request.form["ten"].strip() + " chiều đi",
                            "id": "app_syncState_" + str(int(time.time())),
                            "trigger":
                            {
                                "entity_id": entity1,
                                "platform": "state"
                            },
                            "action":
                            {
                                "entity_id": entity2,
                                "service_template": "{% if states." + entity1.replace('switch.', 'switch[\'') + "'].state == 'on' %}\n  " + entity2.split(".")[0] + ".turn_on\n{% else %}\n" + entity2.split(".")[0] + ".turn_off\n{% endif %}   \n"
                            }
                        },
                            {
                            "alias": request.form["ten"].strip() + " chiều về",
                            "id": "app_syncState_" + str(int(time.time()) + 1),
                            "trigger": {
                                "entity_id": entity2,
                                "platform": "state"
                            },
                            "action":
                            {
                                "entity_id": entity1,
                                "service_template": "{% if states." + entity2.replace('switch.', 'switch[\'') + "'].state == 'on' %}\n  " + entity1.split(".")[0] + ".turn_on\n{% else %}\n" + entity1.split(".")[0] + ".turn_off\n{% endif %}   \n"
                            }
                        }]
                    list_automation = [i for i in list_automation if not (i['id'].find(
                        iden) != -1 or i['id'].find(add_timestamp(iden)) != -1 or i['id'].find(sub_timestamp(iden)) != -1)]
                    if type(data) == list:
                        list_automation.extend(data)
                    else:
                        list_automation.append(data)
                    dict2yaml(list_automation, os.path.join(
                        ROOT_DIR, 'automations.yaml'))
                    list_devices = get_devices()
                    list_entity_id = [i['entity_id'] for i in list_devices]
                    list_entity_name = []
                    for i in list_devices:
                        try:
                            if(i['attributes'].get('device_class') == 'tv'):
                                list_entity_name.append(
                                    'TV: ' + i['attributes']['friendly_name'])
                            else:
                                list_entity_name.append(
                                    i['attributes']['friendly_name'])
                        except:
                            list_entity_name.append('Thiết bị không có tên')
                    list_entity_id, list_entity_name = zip(
                        *sorted(zip(list_entity_id, list_entity_name)))
                    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')

                    # restart automation luôn
                    restart_automation()
                    return show_automation()
                elif iden.find("app_timer_") != -1:
                    entity_id = request.form['entity'].split(
                        '(')[1].split(')')[0]
                    service = request.form["action"]
                    if service == 'climate.set_temperature':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "hvac_mode": request.form['mode'],
                                "temperature": request.form['temperature']
                            },
                            "service": service
                        }]
                    elif service == 'climate.set_fan_mode':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "fan_mode": request.form['fan_mode']
                            },
                            "service": service
                        }]
                    elif service == 'cover.set_cover_position':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "position": request.form['pct_open']
                            },
                            "service": service
                        }]
                    elif service == 'light.turn_on':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "color_name": request.form['color']
                            },
                            "service": service
                        }]
                    elif service == 'media_player.volume_set':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "volume_level": request.form['volume']
                            },
                            "service": service
                        }]
                    elif service == 'media_player.select_source':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "source": request.form['source']
                            },
                            "service": service
                        }]
                    elif service == 'media_player.speak':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "message": request.form['message']
                            },
                            "service": 'tts.google_translate_say'
                        }]
                    elif service.split('.')[0] == 'alarm_control_panel':
                        action_data = [{
                            "data": {
                                "entity_id": entity_id,
                                "code": int(request.form['alarm_code'])
                            },
                            "service": service
                        }]
                    else:
                        action_data = [{
                            "data": {
                                "entity_id": entity_id
                            },
                            "service": service
                        }]
                    day_in_week = ["mon", "tue", "wed",
                                   "thu", "fri", "sat", "sun"]
                    list_day = []
                    for i in day_in_week:
                        try:
                            request.form[i]
                            list_day.append(i)
                        except:
                            pass
                            # print("Cannot get", i)
                    data = {
                        "action": action_data,
                        "alias": request.form["ten"],
                        "condition": [{
                            "condition": "time",
                            "weekday": list_day
                        }] if list_day != [] else [],
                        "id": "app_timer_" + str(int(time.time())),
                        "trigger": [
                            {
                                "at": request.form["time"],
                                "platform": "time"
                            }
                        ]
                    }
                    list_automation = yaml2dict(
                        os.path.join(ROOT_DIR, 'automations.yaml'))
                    list_automation = [
                        i for i in list_automation if i["id"] != iden]
                    list_automation.append(data)
                    dict2yaml(list_automation, os.path.join(
                        ROOT_DIR, 'automations.yaml'))
                    list_entity_id = []
                    list_devices = get_devices()
                    list_services = get_services()
                    for i in list_devices:
                        list_entity_id.append(i['entity_id'])

                    restart_automation()
                    return show_automation()
                elif iden.find("tts_nhaclich") != -1:
                    day_in_week = ["mon", "tue", "wed",
                                   "thu", "fri", "sat", "sun"]
                    list_day = []
                    for i in day_in_week:
                        try:
                            if (request.form[i] != 0):
                                list_day.append(i)
                        except:
                            pass
                    try:
                        data = {
                            "action": [{
                                "service": "tts.google_translate_say",
                                "data": {
                                    "message": request.form["msg"],
                                    "entity_id": request.form["entity_id"].split("(")[-1][:-1]
                                }
                            }],
                            "alias": request.form["ten"],
                            "condition": [{
                                "condition": "time",
                                "weekday": list_day
                            },
                                {
                                "condition": "state",
                                "entity_id": request.form["door_sensor"].split("(")[-1][:-1],
                                "state": request.form["state"]
                            }] if list_day != [] else [],
                            "id": "tts_nhaclich." + str(uuid.uuid4()).replace("-", ""),
                            "trigger": [
                                {
                                    "at": request.form["time"],
                                    "platform": "time"
                                }
                            ]
                        }
                    except:
                        data = {
                            "action": [{
                                "service": "tts.google_translate_say",
                                "data": {
                                    "message": request.form["msg"],
                                    "entity_id": request.form["entity_id"].split("(")[-1][:-1]
                                }
                            }],
                            "alias": request.form["ten"],
                            "condition": [{
                                "condition": "time",
                                "weekday": list_day
                            }] if list_day != [] else [],
                            "id": "tts_nhaclich." + str(uuid.uuid4()).replace("-", ""),
                            "trigger": [
                                {
                                    "at": request.form["time"],
                                    "platform": "time"
                                }
                            ]
                        }
                    list_automation = yaml2dict(os.path.join(
                        ROOT_DIR, 'automations.yaml'))
                    list_automation = [
                        i for i in list_automation if (i['id'] != iden)]
                    list_automation.append(data)
                    dict2yaml(list_automation, os.path.join(
                        ROOT_DIR, 'automations.yaml'))
                    restart_automation()
                    return show_automation()
                else:
                    data = {}
                    data['id'] = iden
                    data['alias'] = request.form['ten']
                    data['trigger'] = deal_with_trigger()
                    data['condition'] = deal_with_condition()
                    data['action'] = deal_with_action()

                    with open("data_file.json", "w") as write_file:
                        json.dump(data, write_file)
                    f = open('data_file.json', 'r')
                    data = json.load(f)
                    list_automation = yaml2dict(
                        os.path.join(ROOT_DIR, 'automations.yaml'))
                    list_automation = [
                        i for i in list_automation if i['id'] != iden]
                    list_automation.append(data)
                    dict2yaml(list_automation, os.path.join(
                        ROOT_DIR, 'automations.yaml'))
                    list_entity_id = []
                    list_devices = get_devices()
                    for i in list_devices:
                        list_entity_id.append(i['entity_id'])

                    restart_automation()
                    return show_automation()
        else:
            return render_template('./login.html', err='')
    else:
        return render_template('./login.html', err='')


@mod.route('/add_tracker_automation', methods=['GET', 'POST'])
def add_tracker_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                return render_template('./add_tracker_automation.html', list_entity_id=list_entity_id)
            else:
                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                check_exist(filename)
                data = {}
                data['id'] = str(int(time.time()))
                data['alias'] = request.form['ten']
                data['trigger'] = []
                data['trigger'].append({
                    'platform': 'state',
                    'entity_id': request.form['entity_id'],
                    'to': request.form['tostate'],
                    'from': request.form['fromstate'],
                    'for': '00:' + request.form['time'] + ':00'
                })
                data['action'] = [{'service': 'homeassistant.restart'}]
                automations = yaml2dict(filename)
                automations.append(data)
                dict2yaml(automations, filename)

                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/add_dongbo', methods=['GET', 'POST'])
def add_dongbo():
    if 'logged_in' in session:
        if session['logged_in'] == False:
            render_template('./login.html', error='')
        if request.method == 'GET':
            list_devices = get_devices()
            list_entity_id = [i['entity_id'] for i in list_devices]
            list_entity_name = []
            for i in list_devices:
                try:
                    if(i['attributes'].get('device_class') == 'tv'):
                        list_entity_name.append(
                            'TV: ' + i['attributes']['friendly_name'])
                    else:
                        list_entity_name.append(
                            i['attributes']['friendly_name'])
                except:
                    list_entity_name.append('Thiết bị không có tên')
            list_entity_id, list_entity_name = zip(
                *sorted(zip(list_entity_id, list_entity_name)))
            return render_template('./automation/add_dongbo.html', list_entity_id=list_entity_id, list_entity_name=list_entity_name)
        else:
            list_automation = yaml2dict(
                os.path.join(ROOT_DIR, 'automations.yaml'))
            kieu = request.form['type']
            entity1 = request.form["entity1"].split("(")[1][:-1]
            entity2 = request.form["entity2"].split("(")[1][:-1]
            # print(entity1, entity2)
            if kieu.find("một chiều") != -1:
                data = {
                    "alias": request.form["ten"],
                    "id": "app_syncState_" + str(int(time.time())),
                    "trigger": {
                        "entity_id": entity1,
                        "platform": "state"
                    },
                    "action": {
                        "entity_id": entity2,
                        "service_template": "{% if is_state('" + entity1 + "','on') %} switch.turn_on {% else %} switch.turn_off {% endif %}"
                    }
                }
            else:
                value_template_1 = "{{ is_state('" + entity2 + "', 'off')}}"
                # print(value_template_1)
                idx = str(int(time.time()))
                data = [{
                    "alias": request.form["ten"] + "_1",
                    "id": "app_syncState_" + idx + "_1",
                    "trigger":[
                        {
                            "entity_id": entity1,
                            "platform": "state",
                                        "to": "on"
                        }],
                    "action": [
                        {
                            "service": "switch.turn_on",
                            "data": {
                                "entity_id": entity2,
                            }

                        }],
                    "condition":
                    {
                        "condition": "template",
                        "value_template": "{{ is_state('"+entity2+"', 'off') }}",
                    }
                },
                    {
                    "alias": request.form["ten"] + "_2",
                    "id": "app_syncState_" + idx + "_2",
                    "trigger":
                    {
                        "entity_id": entity1,
                        "platform": "state",
                        "to": "off"
                    },
                    "action":
                    [{
                        "service": "switch.turn_off",
                        "data": {
                            "entity_id": entity2,
                        }

                    }],
                    "condition":
                    {
                        "condition": "template",
                        "value_template": "{{ is_state('"+entity2+"', 'on') }}",
                    }
                },
                    {
                    "alias": request.form["ten"] + "_3",
                    "id": "app_syncState_" + idx + "_3",
                    "trigger":
                    {
                        "entity_id": entity2,
                        "platform": "state",
                        "to": "on"
                    },
                    "action":
                    [{
                        "service": "switch.turn_on",
                        "data": {
                            "entity_id": entity1,
                        }
                    }],
                    "condition":
                    {
                        "condition": "template",
                        "value_template": "{{ is_state('"+entity1+"', 'off') }}",
                    }
                },
                    {
                    "alias": request.form["ten"] + "_4",
                    "id": "app_syncState_" + idx + "_4",
                    "trigger":
                    {
                        "entity_id": entity2,
                        "platform": "state",
                        "to": "off"
                    },
                    "action":
                    [{
                        "service": "switch.turn_off",
                        "data": {
                            "entity_id": entity1,
                        }
                    }],
                    "condition":
                    {
                        "condition": "template",
                        "value_template": "{{ is_state('"+entity1+"', 'on') }}",
                    }
                },
                ]
            if type(data) == list:
                list_automation.extend(data)
            else:
                list_automation.append(data)
            dict2yaml(list_automation, os.path.join(
                ROOT_DIR, 'automations.yaml'))
            list_devices = get_devices()
            list_entity_id = [i['entity_id'] for i in list_devices]
            list_entity_name = []
            for i in list_devices:
                try:
                    if(i['attributes'].get('device_class') == 'tv'):
                        list_entity_name.append(
                            'TV: ' + i['attributes']['friendly_name'])
                    else:
                        list_entity_name.append(
                            i['attributes']['friendly_name'])
                except:
                    list_entity_name.append('Thiết bị không có tên')
            list_entity_id, list_entity_name = zip(
                *sorted(zip(list_entity_id, list_entity_name)))
            secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')

            # restart automation luôn
            restart_automation()
            return show_automation()
    else:
        render_template('./login.html', error='')


@mod.route('/add_climate_automation', methods=['GET', 'POST'])
def add_climate_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = [i['entity_id'] for i in list_devices]
                return render_template('./automation/add_climate_automation.html', list_entity_id=list_entity_id)
            else:
                name = request.form["ten"]
                entity_id = request.form["entity_id"]
                min_temp = request.form["min_temp"]
                max_temp = request.form["max_temp"]
                temp_step = request.form["temp_step"]
                start_time = request.form["start_time"]
                time_step = request.form["time_step"]
                list_au = gen_climate_automation_content(name, entity_id, int(
                    min_temp), int(max_temp), int(temp_step), start_time, int(time_step))
                au_file = os.path.join(ROOT_DIR, 'automations.yaml')
                list_automation = yaml2dict(au_file)
                for i in list_au:
                    list_automation.append(i)
                dict2yaml(list_automation, au_file)
                # restart automation luon
                restart_automation()
                return show_automation()


@mod.route('/add_lock', methods=['GET', 'POST'])
def add_lock():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = []
                list_entity_name = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                list_services = get_services()
                result_service = {}
                result_list_service = []
                for ser in list_services:
                    for en in list_entity_id:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                file_dir = os.path.join(
                    ROOT_DIR, '.storage', 'core.restore_state')
                for i in result_service:
                    for j in result_service[i]:
                        result_list_service.append(i+"."+j)
                # print(result_list_service)
                result_list_service.sort()
                # list_entity_id = sorted(list_entity_id)
                return render_template('./automation/add_lock.html', list_entity_name=list_entity_name,
                                       list_entity_id=list_entity_id, list_services=result_list_service)
            elif request.method == 'POST':
                data = {}
                data['id'] = 'lock_' + str(int(time.time()))
                data['alias'] = request.form['ten']
                # trigger
                data['trigger'] = []
                trigger = request.form['trigger']
                data['trigger'].append({
                    "platform": "mqtt",
                    "topic": 'zigbee2mqtt/' + trigger.split('.')[1].split('_')[0]
                })
                # condition
                data['condition'] = []
                after = str(request.form["after"])
                before = str(request.form["before"])
                if after == "":
                    if before != "":
                        data['condition'].append({
                            "condition": "time",
                            "before": before if before != "24:00" else "00:00"
                        })
                else:
                    if before == "":
                        data['condition'].append({
                            "condition": "time",
                            "after": after if after != "24:00" else "00:00"
                        })
                    else:
                        data['condition'].append({
                            "condition": "time",
                            "after": after if after != "24:00" else "00:00",
                            "before": before if before != "24:00" else "00:00"
                        })
                touch_lock = request.form['touch_lock']
                rfid_lock = request.form['rfid_lock']
                passcode_lock = request.form['passcode_lock']
                list_string = []
                string_ = ''

                if (touch_lock != ''):
                    for i in touch_lock:
                        list_string.append(
                            '((trigger.payload_json["action_source_name"] == "touch_unlock") and (trigger.payload_json["action_user"] == ' + i + '))')
                if (passcode_lock != ''):
                    for i in passcode_lock:
                        list_string.append(
                            '((trigger.payload_json["action_source_name"] == "keypad") and (trigger.payload_json["action_user"] == ' + i + '))')
                if (rfid_lock != ''):
                    for i in rfid_lock:
                        list_string.append(
                            '((trigger.payload_json["action_source_name"] == "rfid_card_unlock") and (trigger.payload_json["action_user"] == ' + i + '))')
                for i in range(len(list_string)):
                    if (i < len(list_string) - 1):
                        string_ += list_string[i] + ' or '
                    else:
                        string_ += list_string[i]

                data["condition"].append({
                    "condition": "template",
                    "value_template": '{{ ' + string_ + ' }}'
                })
                # action
                data['action'] = deal_with_action()

                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                automation.append(data)
                dict2yaml(automation, filename)

                # restart automation luon
                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/edit_lock', methods=['GET', 'POST'])
def edit_lock():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                iden = request.args.get('iden')
                list_devices = get_devices()
                list_entity_id = []
                list_entity_name = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                list_services = get_services()
                result_service = {}
                result_list_service = []
                for ser in list_services:
                    for en in list_entity_id:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                file_dir = os.path.join(
                    ROOT_DIR, '.storage', 'core.restore_state')
                for i in result_service:
                    for j in result_service[i]:
                        result_list_service.append(i+"."+j)
                # print(result_list_service)
                result_list_service.sort()
                # list_entity_id = sorted(list_entity_id)
                iden = request.args.get('iden')
                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                lock_automation = [i for i in automation if i['id'] == iden]
                # --------------action-----------------
                list_action_name = []
                list_action = []
                delay = []
                for j in lock_automation[0]['action']:
                    if 'delay' in j:
                        delay.append(j['delay'])
                    else:
                        try:
                            list_action_name.append(list_entity_name[[i for i in range(
                                len(list_entity_id)) if list_entity_id[i] == j['data']["entity_id"]][0]])
                        except Exception:
                            list_action_name.append(
                                "Thiết bị không có tên")
                        list_action.append(j)
                len_dict = len(list_action)
                count_loop = 0
                for i in list_action:
                    count_loop += 1
                    i['data']['entity_id'] = list_action_name[count_loop -
                                                              1] + ' (' + i['data']['entity_id'] + ')'
                    if (i['service'] == 'media_player.volume_set'):
                        i['data']['volume_level'] = int(
                            i['data']['volume_level'] * 100)

                list_entities = []
                cnt_loop = 0
                for i in list_entity_id:
                    cnt_loop += 1
                    list_entities.append(
                        list_entity_name[cnt_loop - 1] + ' (' + list_entity_id[cnt_loop-1] + ')')
                len_dict = len(list_action)
                return render_template('./automation/edit_lock.html', list_entity_name=list_entity_name, list_action=list_action, delay=delay, len_dict=len_dict,
                                       list_entity_id=list_entity_id, list_services=result_list_service, lock_automation=lock_automation[0], iden=iden)
            elif request.method == 'POST':
                data = {}
                iden = request.args.get('iden')
                data['id'] = iden
                data['alias'] = request.form['ten']
                # trigger
                data['trigger'] = []
                trigger = request.form['trigger']
                data['trigger'].append({
                    "platform": "mqtt",
                    "topic": 'zigbee2mqtt/' + trigger.split('.')[1].split('_')[0]
                })
                # condition
                data['condition'] = []
                touch_lock = request.form['touch_lock']
                rfid_lock = request.form['rfid_lock']
                passcode_lock = request.form['passcode_lock']
                list_string = []
                string_ = ''
                if (touch_lock != ''):
                    list_string.append(
                        '((trigger.payload_json["action_source_name"] == "touch_unlock") and (trigger.payload_json["action_user"] == ' + touch_lock + "))")
                if (passcode_lock != ''):
                    list_string.append(
                        '((trigger.payload_json["action_source_name"] == "keypad") and (trigger.payload_json["action_user"] == ' + passcode_lock + "))")
                if (rfid_lock != ''):
                    list_string.append(
                        '((trigger.payload_json["action_source_name"] == "rfid_card_unlock") and (trigger.payload_json["action_user"] == ' + rfid_lock + "))")
                for i in range(len(list_string)):
                    if (i < len(list_string) - 1):
                        string_ += list_string[i] + ' or '
                    else:
                        string_ += list_string[i]

                data["condition"].append({
                    "condition": "template",
                    "value_template": '{{ ' + string_ + ' }}'
                })
                # action
                data['action'] = deal_with_action()

                with open("data_file.json", "w") as write_file:
                    json.dump(data, write_file)
                f = open('data_file.json', 'r')
                data = json.load(f)
                list_automation = yaml2dict(
                    os.path.join(ROOT_DIR, 'automations.yaml'))
                list_automation = [
                    i for i in list_automation if i['id'] != iden]
                list_automation.append(data)
                dict2yaml(list_automation, os.path.join(
                    ROOT_DIR, 'automations.yaml'))
                # restart automation luon
                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route("/add_repeat_automation", methods=['GET', 'POST'])
def add_repeat_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = []
                list_entity_name = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                list_entitys = []
                for i in range(len(list_entity_id)):
                    if list_entity_id[i].split('.')[0] != 'automation':
                        list_entitys.append(
                            list_entity_name[i] + ' (' + list_entity_id[i] + ')')
                return render_template("automation/repeat_automation.html", list_entitys=list_entitys)
            else:
                data = {}
                type_ = request.form['time_trigger']
                data['id'] = str(int(time.time())) + '_' + type_ + '_notices'
                data['alias'] = request.form['ten']

                # condition
                data['condition'] = deal_with_condition()
                try:
                    hour = request.form['Hour']
                    minute = request.form['Minute']
                    second = request.form['Second']
                    if ((type_ == 'monthly') or (type_ == 'yearly')):
                        if ((type_ == 'monthly')):
                            condition = [{
                                'condition': 'template',
                                'value_template': "{{ now().day == " + request.form['Date'] + " }}"
                            }]
                        else:
                            condition = [{
                                'condition': 'template',
                                'value_template': "{{ now().day == " + request.form['Date'] + " }}"
                            }, {
                                'condition': 'template',
                                'value_template': "{{ now().month == " + request.form['Month'] + " }}"
                            }]

                        data['condition'] = data['condition'] + condition
                        data['trigger'] = [{
                            'platform': 'time',
                            'at': hour + ':' + minute + ':' + second
                        }]
                    elif ((type_ == 'custom')):
                        daily_con = {'platform': 'time_pattern'}
                        if (hour != '00'):
                            daily_con['hours'] = '/' + hour
                        if (minute != '00'):
                            daily_con['minutes'] = '/' + minute
                        if (second != '00'):
                            daily_con['seconds'] = '/' + second
                        data['trigger'] = [daily_con]
                        data['condition'] = data['condition']
                    else:
                        data['trigger'] = [{
                            'platform': 'time',
                            'at': hour + ':' + minute + ':' + second
                        }]
                        data['condition'] = data['condition']
                except Exception as error:
                    # print(error)
                    pass
                # action
                data['action'] = {"data": {
                    "entity_id": request.form['speaker'].split('(')[1][:-1], 'message': request.form['message']}, "service": 'tts.google_translate_say'}

                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                automation.append(data)
                dict2yaml(automation, filename)
                # restart automation luon
                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route("/edit_repeat_automation", methods=['GET', 'POST'])
def edit_repeat_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                iden = request.args.get('id')
                data_file = yaml2dict(os.path.join(
                    ROOT_DIR, 'automations.yaml'))
                repeat_automation_data = [
                    i for i in data_file if (i['id'] == iden)]
                data = repeat_automation_data[0]

                list_devices = get_devices()
                list_entity_id = []
                list_entity_name = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                    try:
                        if(i['attributes'].get('device_class') == 'tv'):
                            list_entity_name.append(
                                'TV: ' + i['attributes']['friendly_name'])
                        else:
                            list_entity_name.append(
                                i['attributes']['friendly_name'])
                    except:
                        list_entity_name.append('Thiết bị không có tên')
                list_entity_id, list_entity_name = zip(
                    *sorted(zip(list_entity_id, list_entity_name), key=lambda x: x[1]))
                list_entitys = []
                for i in range(len(list_entity_id)):
                    if list_entity_id[i].split('.')[0] != 'automation':
                        list_entitys.append(
                            list_entity_name[i] + ' (' + list_entity_id[i] + ')')
                condition = data['condition']
                list_condition = [i for i in condition if (
                    i.get('value_template') == None)]
                return render_template("automation/edit_repeat_automation.html", list_entitys=list_entitys, data=data, list_condition=list_condition)
            else:
                print(request.form)
                iden = request.args.get('iden')
                data = {}
                data['id'] = str(int(time.time())) + '_notices'
                data['alias'] = request.form['ten']

                type_ = request.form['time_trigger']
                # condition
                data['condition'] = deal_with_condition()
                try:
                    hour = request.form['Hour']
                    minute = request.form['Minute']
                    second = request.form['Second']
                    if ((type_ == 'monthly') or (type_ == 'yearly')):
                        if ((type_ == 'monthly')):
                            condition = [{
                                'condition': 'template',
                                'value_template': "{{ now().day == " + request.form['Date'] + " }}"
                            }]
                        else:
                            condition = [{
                                'condition': 'template',
                                'value_template': "{{ now().day == " + request.form['Date'] + " }}"
                            }, {
                                'condition': 'template',
                                'value_template': "{{ now().month == " + request.form['Month'] + " }}"
                            }]

                        data['condition'] = data['condition'] + condition
                        data['trigger'] = [{
                            'platform': 'time',
                            'at': hour + ':' + minute + ':' + second
                        }]
                    elif ((type_ == 'custom')):
                        daily_con = {'platform': 'time_pattern'}
                        if (hour != '00'):
                            daily_con['hours'] = '/' + hour
                        if (minute != '00'):
                            daily_con['minutes'] = '/' + minute
                        if (second != '00'):
                            daily_con['seconds'] = '/' + second
                        data['trigger'] = [daily_con]
                        data['condition'] = data['condition']
                    else:
                        data['trigger'] = [{
                            'platform': 'time',
                            'at': hour + ':' + minute + ':' + second
                        }]
                        data['condition'] = data['condition']
                except Exception as error:
                    # print(error)
                    pass
                # action
                data['action'] = {"data": {
                    "entity_id": request.form['speaker'].split('(')[1][:-1], 'message': request.form['message']}, "service": 'tts.google_translate_say'}

                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                automation = [i for i in automation if (i['id'] != iden)]
                automation.append(data)
                dict2yaml(automation, filename)
                # restart automation luon
                restart_automation()
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')
