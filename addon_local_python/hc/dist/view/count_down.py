from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from view.automation import show_automation
from utils import *
mod = Blueprint('count_down', __name__)


@mod.route('/count_down', methods=['GET'])
def show_count_down():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            try:
                climate_file = os.path.join(ROOT_DIR, 'climate.yaml')
                check_exist(climate_file)
                list_climate = yaml2dict(climate_file)
                return render_template('./count_down/count_down_home.html')
            except:
                return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_count_down', methods=['GET'])
def add_count_down():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            secrets_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            data = yaml2dict(secrets_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            try:
                res_entity = requests.get(
                    URL_STATE, headers=headers)
                list_entity = res_entity.json()
                entitys = []
                domains = []
                result_entity = []
                result_service = {}
                result_list_service = []
                support_device = ['switch', 'fan', 'climate', 'binary_sensor']
                for en in list_entity:
                    if en['entity_id'].split(".")[0] in support_device:
                        if "friendly_name" in en["attributes"].keys():
                            entitys.append(
                                en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
                res_service = requests.get(
                    URL_SERVICE, headers=headers)
                list_service = res_service.json()
                for ser in list_service:
                    for en in entitys:
                        if re.search(ser['domain'], en):
                            if ser['domain'] not in result_service:
                                result_service[ser['domain']] = [
                                    i for i in ser['services'].keys()]
                            result_entity.append(en)

            except requests.exceptions.ConnectionError:
                result_entity = []
                result_service = []
            for i in result_service:
                for j in result_service[i]:
                    result_list_service.append(i+"."+j)
            result_entity.sort()
            entitys.sort()
            result_list_service.sort()
            return render_template('./count_down/add_count_down.html', entitys=entitys, list_entity=result_entity, list_service=result_list_service)


@mod.route('/add_count_down', methods=["POST"])
def add_count_down_result():
    if request.method == 'POST':
        data_start = {}
        data_finish = {}
        idx = str(int(time.time()))
        timer_path = os.path.join(ROOT_DIR, 'timer.yaml')
        timer = yaml2dict(timer_path)
        if (str(type(timer)) == "<class 'list'>"):
            timer = {}
        else:
            try:
                timer[idx] = {"duration": request.form['time']}
            except:
                timer = {}
                timer[idx] = {"duration": request.form['time']}
        dict2yaml(timer, timer_path)

        automation_path = os.path.join(ROOT_DIR, 'automations.yaml')
        automation = yaml2dict(automation_path)
        trigger_st = []
        trigger_start = {}
        trigger_start['platform'] = "state"
        trigger_start['entity_id'] = request.form['entity_trigger'].split('(')[
            1].replace(')', '')
        try:
            trigger_start['from'] = request.form['trigger_fromstate']
        except:
            pass
        trigger_start['to'] = request.form['trigger_tostate']
        trigger_st.append(trigger_start)
        action_finish = []
        action_finish.append(
            {
                "data": {'entity_id': request.form['entity_action'].split('(')[1].replace(')', '')},
                'service': request.form['service']
            }
        )
        action_start = []
        action_start.append(
            {
                'entity_id': "timer."+idx,
                'service': "timer.start"
            }
        )
        data_start['action'] = action_start
        data_start['alias'] = request.form['name'] + ' bắt đầu'
        data_start['id'] = idx+'.start'
        data_start['trigger'] = trigger_st
        automation.append(data_start)
        data_finish = {}
        trigger_finish = []
        trigger_finish.append(
            {
                "event_data": {"entity_id": "timer."+idx},
                "event_type": "timer.finished",
                "platform": "event"
            }
        )

        data_finish['action'] = action_finish
        data_finish['alias'] = request.form['name'] + " kết thúc"
        data_finish['trigger'] = trigger_finish
        data_finish['id'] = idx+'.finish'

        automation.append(data_finish)
        dict2yaml(automation, automation_path)
        restart_automation()
    return show_automation()


@mod.route('/edit_count_down', methods=['GET'])
def edit_count_down():
    if request.method == 'GET':
        id_item = str(request.args.get('id_timer')).split('.')[0]
        automation_path = os.path.join(ROOT_DIR, 'automations.yaml')
        automation = yaml2dict(automation_path)
        timer_path = os.path.join(ROOT_DIR, 'timer.yaml')
        timer = yaml2dict(timer_path)
        time = timer[id_item.strip()]['duration']
        # new_list = [i for i in list_automation if 'id' in i if i['id'] != iden]
        trigger = []
        action = []
        name = None
        for auto in automation:
            if auto['id'].find(id_item+'.start') != -1:
                trigger = auto['trigger'][0]
                name = auto['alias'].replace(" bắt đầu", "")
            if auto['id'].find(id_item+'.finish') != -1:
                action = auto['action'][0]
        # print(trigger[0]['entity_id'])
        secrets_file = os.path.join(ROOT_DIR, 'secrets.yaml')
        data = yaml2dict(secrets_file)
        authen_code = data['token']
        headers = {
            "Authorization": "Bearer " + authen_code,
            "content-type": "application/json"
        }
        try:
            res_entity = requests.get(
                URL_STATE, headers=headers)
            list_entity = res_entity.json()
            entitys = []
            domains = []
            result_entity = []
            result_service = {}
            result_list_service = []
            support_device = ['switch', 'fan', 'climate', 'binary_sensor']
            for en in list_entity:
                if en['entity_id'].split(".")[0] in support_device:
                    if "friendly_name" in en["attributes"].keys():
                        entitys.append(
                            en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
            res_service = requests.get(
                URL_SERVICE, headers=headers)
            list_service = res_service.json()
            for ser in list_service:
                for en in entitys:
                    if re.search(ser['domain'], en):
                        if ser['domain'] not in result_service:
                            result_service[ser['domain']] = [
                                i for i in ser['services'].keys()]
                        result_entity.append(en)

        except requests.exceptions.ConnectionError:
            result_entity = None
            result_service = None
        for i in result_service:
            for j in result_service[i]:
                result_list_service.append(i+"."+j)
        result_entity.sort()
        entitys.sort()
        result_list_service.sort()
        return render_template('./count_down/edit_count_down.html', trigger=trigger, action=action, name=name, time=time, entitys=entitys, list_entity=result_entity, list_service=result_list_service, id_item=id_item)


@mod.route("/edit_count_down_result", methods=['POST'])
def edit_count_down_redult():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            data_start = {}
            data_finish = {}
            timer = {}
            idx = str(request.args.get('id_item'))
            duration = str(request.form['time'])
            timer_path = os.path.join(ROOT_DIR, 'timer.yaml')
            timer = yaml2dict(timer_path)
            if (str(type(timer)) == "<class 'list'>"):
                timer = {}
            else:
                timer[idx] = {"duration": request.form['time']}
            dict2yaml(timer, timer_path)

            automation_path = os.path.join(ROOT_DIR, 'automations.yaml')
            automation = yaml2dict(automation_path)

            new_list = [i for i in automation if 'id' in i if i['id']
                        != (idx+'.start') and i['id'] != (idx+'.finish')]
            trigger_st = []
            trigger_start = {}
            trigger_start['platform'] = "state"

            trigger_start['entity_id'] = request.form['entity_trigger'].split('(')[
                1].replace(')', '')
            # print(request.form)
            trigger_start['from'] = request.form['trigger_fromstate']
            trigger_start['to'] = request.form['trigger_tostate']

            trigger_st.append(trigger_start)

            action_finish = []
            action_finish.append(
                {
                    "data": {'entity_id': request.form['entity_action'].split('(')[1].replace(')', '')},
                    'service': request.form['service']
                }
            )
            action_start = []
            action_start.append(
                {
                    'entity_id': "timer."+idx,
                    'service': "timer.start"
                }
            )
            data_start['action'] = action_start
            data_start['alias'] = request.form['name'] + ' bắt đầu'
            data_start['id'] = idx+'.start'
            data_start['trigger'] = trigger_st
            new_list.append(data_start)
            data_finish = {}
            trigger_finish = []
            trigger_finish.append(
                {
                    "event_data": {"entity_id": "timer."+idx},
                    "event_type": "timer.finished",
                    "platform": "event"
                }
            )

            data_finish['action'] = action_finish
            data_finish['alias'] = request.form['name'] + " kết thúc"
            data_finish['trigger'] = trigger_finish
            data_finish['id'] = idx+'.finish'

            new_list.append(data_finish)
            dict2yaml(new_list, automation_path)
            restart_automation()
            return show_automation()


@mod.route('/delete_count_down')
def delete_count_down():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            idx = str(request.args.get('id_timer')).split('.')[0].strip()
            automation_path = os.path.join(ROOT_DIR, 'automations.yaml')
            automation = yaml2dict(automation_path)
            new_list = [i for i in automation if 'id' in i if i['id']
                        != (idx+'.start') and i['id'] != (idx+'.finish')]
            dict2yaml(new_list, automation_path)

            timer_path = os.path.join(ROOT_DIR, 'timer.yaml')
            timer = yaml2dict(timer_path)
            try:
                del(timer[idx])
            except:
                pass
            dict2yaml(timer, timer_path)
            restart_automation()
            return show_automation()
