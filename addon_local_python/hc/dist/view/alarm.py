from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
from view.automation import show_automation
import time
mod = Blueprint('alarm', __name__)


@mod.route('/alarm')
def alarm():
    if 'logged_in' in session:
        info = request.args.get('info')
        if session['logged_in'] == True:
            if info != None:
                info = "Thêm thiết bị thành công."
            filename = os.path.join(ROOT_DIR, 'alarm.yaml')
            check_exist(filename)
            list_alarm = yaml2dict(filename)
            list_id = [no_accent_vietnamese(i['name'].replace(
                " ", "_")).lower() for i in list_alarm]

            filename = os.path.join(ROOT_DIR, 'automations.yaml')
            check_exist(filename)
            list_automation = yaml2dict(filename)
            list_automation = [i for i in list_automation if (i.get('alias') == 'armed_away') or (i.get(
                'alias') == 'armed_home') or (i.get('alias') == 'disarmed') or (i.get('alias') == 'triggered')]

            return render_template('./alarm/alarm.html', list_alarm=list_alarm, list_id=list_id, info=info, list_automation=list_automation)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/add_alarm', methods=['GET', 'POST'])
def add_alarm():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                return render_template('./alarm/add_alarm.html')
            else:
                # print(request.form)
                list_alarm = []
                # list_alarm = yaml2dict(os.path.join(ROOT_DIR, 'alarm.yaml'))
                data = {}
                data['platform'] = 'manual'
                data['name'] = request.form['name']
                data['code'] = request.form['password']
                arming_time = request.form['arming_time']
                if arming_time != "" and arming_time.isdigit():
                    data['arming_time'] = int(arming_time)
                delay_time = request.form["delay_time"]
                if delay_time != "" and delay_time.isdigit():
                    data['delay_time'] = int(delay_time)
                trigger_time = request.form["trigger_time"]
                if trigger_time != "" and trigger_time.isdigit():
                    data['trigger_time'] = int(trigger_time)
                data["disarmed"] = {
                    "trigger_time": 0
                }
                data["armed_home"] = {
                    "arming_time": 0,
                    "delay_time": 0
                }
                list_alarm.append(data)
                dict2yaml(list_alarm, os.path.join(ROOT_DIR, 'alarm.yaml'))
                return alarm()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/delete_alarm', methods=['POST'])
def delete_alarm():
    iden = request.args.get('iden')
    list_alarm = yaml2dict(os.path.join(ROOT_DIR, 'alarm.yaml'))
    new_list_alarm = [i for i in list_alarm if no_accent_vietnamese(
        i["name"].replace(" ", "_").lower()) != iden]
    dict2yaml(new_list_alarm, os.path.join(ROOT_DIR, 'alarm.yaml'))
    return alarm()


@mod.route('/edit_alarm', methods=['GET', 'POST'])
def edit_alarm():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            filename = os.path.join(ROOT_DIR, 'alarm.yaml')
            data = yaml2dict(filename)
            return render_template('./alarm/edit_alarm.html', data=data[0])
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/add_alarm_notify', methods=['GET', 'POST'])
def add_notify_alarm():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_devices = get_devices()
                list_entity_id = []
                for i in list_devices:
                    list_entity_id.append(i['entity_id'])
                list_services = get_services()
                # list_services = json.loads(list_services)
                services = []
                for i in list_services:
                    if i["domain"] == "notify":
                        for j in i["services"]:
                            services.append(i["domain"] + "." + j)
                services.append("xiaomi_aqara.play_ringtone")
                # print(services)
                list_xiaomi_gateway = yaml2dict(
                    os.path.join(ROOT_DIR, 'xiaomi_aqara.yaml'))
                # print('list_services: ', list_services)
                # print('list_xiaomi_gateway: ', list_xiaomi_gateway)
                # print('list_entity_id: ', list_entity_id)
                return render_template('./automation/add_alarm_notify.html', list_xiaomi_gateway=list_xiaomi_gateway["gateways"],
                                       list_entity_id=list_entity_id, list_services=services)
            else:
                data = {
                    "alias": request.form['ten'],
                    "id": "alarm." + str(int(time.time())),
                    "trigger": [{
                        "platform": "state",
                        "entity_id": request.form["entity_id"],
                        "to": request.form["tostate"]
                    }],
                }
                service = request.form["service"]
                # print(service)
                if service == "xiaomi_aqara.play_ringtone":
                    data["action"] = [{
                        "service": service,
                        "data": {
                            "gw_mac": request.form['gw_mac'],
                            "ringtone_id": request.form['ringtone_id'],
                            "ringtone_vol": request.form["ringtone_vol"] if request.form["ringtone_vol"] != "" else "50"
                        },
                    }]
                else:
                    data["action"] = [{
                        "service": request.form["service"],
                        "data": {
                            "target": ["email/" + request.form["email"]],
                            "title": request.form["title"],
                            "message": request.form["message"]
                        },
                    }]
                if request.form["after"] != "":
                    data["condition"] = [{
                        "condition": "time",
                        "after": request.form["after"],
                        "before": request.form["before"]
                    }]
                if request.form["trigger_time"] != "":
                    data["trigger"][0]["for"] = "00:" + \
                        request.form["trigger_time"] + ":00"

                filename = os.path.join(ROOT_DIR, 'automations.yaml')
                automation = yaml2dict(filename)
                automation.append(data)
                dict2yaml(automation, filename)

                # restart automation luon
                secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
                url_service = 'http://localhost:8123/api/services/automation/reload'
                data = yaml2dict(secret_file)
                authen_code = data['token']
                headers = {
                    "Authorization": "Bearer " + authen_code,
                    "content-type": "application/json"
                }
                res = requests.post(url_service, headers=headers)
                return show_automation()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/alarm_automation', methods=['GET', 'POST'])
def alarm_automation():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            name = request.args.get('name')
            list_devices = get_devices()
            list_entity_id = []
            for i in list_devices:
                list_entity_id.append(i['entity_id'])
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
            list_services = get_services()

            list_entities = []
            for i in range(len(list_entity_name)):
                list_entities.append(
                    list_entity_name[i] + ' (' + list_entity_id[i] + ')')

            filename = os.path.join(ROOT_DIR, 'automations.yaml')
            list_automation = yaml2dict(filename)

            list_automation = [
                i for i in list_automation if (i.get('alias') == name)]
            # print('automation --> ', name, '-->', list_automation)
            list_trigger = []
            list_action = []
            try:
                list_trigger = list_automation[0]['trigger']
                list_action = list_automation[0]['action']

                for i in range(len(list_trigger)):
                    for j in list_entities:
                        if (j.split('(')[1].split(')')[0] == list_trigger[i]['entity_id']):
                            list_trigger[i]['entity_id'] = j
                for i in range(len(list_action)):
                    for j in list_entities:
                        if (j.split('(')[1].split(')')[0] == list_action[i]['data']['entity_id']):
                            list_action[i]['data']['entity_id'] = j
                    if (list_action[i]['service'] == 'media_player.volume_set'):
                        list_action[i]['data']['volume_level'] = int(
                            list_action[i]['data']['volume_level'] * 100)

                return render_template('./automation/add_alarm_automation.html', list_action=list_action, list_trigger=list_trigger, list_automation=list_automation, list_entity_name=list_entity_name,
                                       list_entity_id=list_entity_id, list_services=list_services, list_entities=list_entities, name=name)
            except Exception as error:
                # print('error: ', error)
                return render_template('./automation/add_new_alarm_automation.html', list_action=list_action, list_trigger=list_trigger, list_automation=list_automation, list_entity_name=list_entity_name,
                                       list_entity_id=list_entity_id, list_services=list_services, list_entities=list_entities, name=name)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/add_alarm_auto', methods=['POST'])
def add_alarm_auto():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            data = {}
            data['id'] = 'alarm.' + str(int(time.time()))
            data['alias'] = request.form['condition_state']
            data['trigger'] = []
            list_trigger = request.form.getlist('trigger')
            list_trigger_above = request.form.getlist('trigger_above')
            list_trigger_below = request.form.getlist('trigger_below')
            list_trigger_fromstate = request.form.getlist(
                'trigger_fromstate')
            list_trigger_tostate = request.form.getlist('trigger_tostate')
            list_trigger_time = request.form.getlist('trigger_time')
            count_trigger_sensor = 0
            count_trigger_other_device = 0
            for i in range(len(list_trigger)):
                if list_trigger[i].split("(")[1][:-1].split(".")[0] in ["sensor"]:
                    data['trigger'].append({
                        'platform': 'numeric_state',
                        'above': list_trigger_above[count_trigger_sensor],
                        'below': list_trigger_below[count_trigger_sensor],
                        'entity_id': list_trigger[i].split("(")[1][:-1]
                    })
                    count_trigger_sensor += 1
                else:
                    data['trigger'].append({
                        'platform': 'state',
                        'to': list_trigger_tostate[count_trigger_other_device].lower() if len(list_trigger_tostate) != 0 else "",
                        'entity_id': list_trigger[i].split("(")[1][:-1]
                    })
                    count_trigger_other_device += 1
            data['condition'] = []
            list_condition = request.form.getlist('condition')
            list_condition_state = request.form.getlist('condition_state')
            list_chose_condition_state = request.form.getlist(
                'chose_condition_state')
            list_condition_above = request.form.getlist('above_condition')
            list_condition_below = request.form.getlist('below_condition')
            count_condition_sensor = 0
            count_condition_other_device = 0
            for i in range(len(list_condition)):
                if list_condition[i].split("(")[1][:-1].split(".")[0] == "sensor":
                    data['condition'].append({
                        "entity_id": list_condition[i].split("(")[1][:-1],
                        "condition": "numeric_state",
                        "above": list_condition_above[count_condition_sensor],
                        "below": list_condition_below[count_condition_sensor]
                    })
                    count_condition_sensor += 1
                else:
                    data['condition'].append({
                        "entity_id": list_condition[i].split("(")[1][:-1],
                        "condition": "state",
                        "state": list_condition_state[count_condition_other_device].lower() if len(list_condition_state) != 0 else ""
                    })
                    count_condition_other_device += 1
                after = str(request.form["after"])
                before = str(request.form["before"])
                if after == "":
                    if before != "":
                        data['condition'].append({
                            "condition": "time",
                            "before": before
                        })
                else:
                    if before == "":
                        data['condition'].append({
                            "condition": "time",
                            "after": after
                        })
                    else:
                        data["condition"].append({
                            "condition": "time",
                            "after": after,
                            "before": before
                        })

            data['action'] = []
            list_entity = request.form.getlist("entity")
            list_service = request.form.getlist("action")

            sequen = []
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
            list_brightness_pct = request.form.getlist('brightness_pct')
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
            for i, j in zip(list_entity, list_service):
                # print(i, j)
                count_loop += 1
                # print('count_loop: ', count_loop-1)
                if (j.find('speak') != -1):
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                    ), 'message': list_message[dem_noi]}, "service": 'tts.google_translate_say'})
                    dem_noi += 1
                elif j.find('media_player.select_source') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(
                        ')', '').strip(), 'source': list_source[dem_tv]},  "service": j})
                    dem_tv += 1
                elif j.find('media_player.volume_set') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(
                        ')', '').strip(), 'volume_level': (int(list_volume[dem_vol])/100)},  "service": j})
                    dem_vol += 1
                elif j.find('climate.set_temperature') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                    ), 'hvac_mode': list_mode[dem_mode], 'temperature': int(list_temp[dem_tem])},  "service": j})
                    dem_tem += 1
                    dem_mode += 1
                elif j.find('climate.set_fan_mode') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                    ), 'fan_mode': list_fan_mode[dem_fan_mode]},  "service": j})
                    dem_fan_mode += 1
                elif j.find('set_cover_position') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                    ), 'position': int(list_pct[dem_pct])},  "service": j})
                    dem_pct += 1
                elif i.find('lock') != -1:
                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(
                        ')', '').strip(), 'code': list_lock_code[dem_lock_code]},  "service": j})
                    dem_lock_code += 1
                elif j.find('light.turn_on') != -1:
                    set_mode = 0
                    try:
                        # print('try 1')
                        if (int(list_brightness_pct_order[dem_brightness_pct]) == (count_loop - 1)):
                            # print('--------->brightness_pct')
                            sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                            ), 'brightness_pct': int(list_brightness_pct[dem_brightness_pct])},  "service": j})
                            dem_brightness_pct += 1
                            set_mode = 1
                    except:
                        try:
                            # print('try 2')
                            if (int(list_color_order[dem_color]) == (count_loop - 1)):
                                # print('--------->color')
                                sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                                ), 'color_name': list_color[dem_color]},  "service": j})
                                dem_color += 1
                                set_mode = 1
                        except:
                            try:
                                # print('try 3')
                                if (int(list_profile_order[dem_profile]) == (count_loop - 1)):
                                    # print('-0-------->profile')
                                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                                    ), 'profile': list_profile[dem_profile]},  "service": j})
                                    dem_profile += 1
                                    set_mode = 1
                            except:
                                print('else')
                    if (set_mode == 0):
                        sequen.append({"data": {"entity_id": i.split(
                            '(')[1].replace(')', '').strip()},  "service": j})
                elif j.find('delay') != -1:
                    sequen.append({"delay": list_delay[dem_delay]})
                    dem_delay += 1
                else:
                    sequen.append({"data": {"entity_id": i.split(
                        '(')[1].replace(')', '').strip()},  "service": j})
            data['action'] = (sequen)

            filename = os.path.join(ROOT_DIR, 'automations.yaml')
            automation = yaml2dict(filename)
            automation = [i for i in automation if (
                i.get('alias') != request.form['condition_state'])]
            automation.append(data)
            dict2yaml(automation, filename)

            # restart automation luon
            secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            url_service = 'http://localhost:8123/api/services/automation/reload'
            data = yaml2dict(secret_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            res = requests.post(url_service, headers=headers)
            return alarm()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')
