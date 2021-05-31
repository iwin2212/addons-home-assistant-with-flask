from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import sort_string_in_list_item
mod = Blueprint('scripts_manager', __name__)


@mod.route('/add_scripts_home')
def add_scripts_home():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            file_name = os.path.join(ROOT_DIR, 'scripts.yaml')
            list_scripts = yaml2dict(file_name)
            res_list = {}
            if list_scripts != None:
                if len(list_scripts) != 0:
                    for lists in list_scripts.keys():
                        if 'alias' in list_scripts[lists]:
                            if int(list_scripts[lists]['alias'].find('Báo nói')) == -1:
                                res_list[lists] = list_scripts[lists]
            return render_template('./scripts_manager/add_scripts_home.html', list_scripts=res_list, err='')
        return render_template('./login.html')
    return render_template('./login.html')


@mod.route('/add_scripts_recall')
def add_scripts_recall():
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
                for en in list_entity:
                    if "friendly_name" in en["attributes"].keys():
                        if(en['attributes'].get('device_class') == 'tv'):
                            entitys.append(
                                'TV: ' + en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
                        else:
                            entitys.append(
                                en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
                res_service = requests.get(URL_SERVICE, headers=headers)
                list_service = res_service.json()
                for ser in list_service:
                    for en in entitys:
                        if re.search(ser['domain'], en):
                            result_entity.append(en)

            except requests.exceptions.ConnectionError:
                result_entity = None
            result_entity = sort_string_in_list_item(result_entity)
            # print('result_entity: ', result_entity)
            return render_template('./scripts_manager/add_scripts_recall.html', list_entitys=result_entity)


@mod.route('/add_scripts_recall', methods=['POST'])
def add_scripts_result():
    # print("hello")
    if request.method == 'POST':
        dict_ = {}
        file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
        dict_ = yaml2dict(file_path)
        if dict_ == None:
            dict_ = {}
        id = 'app_' + str(int(time.time()))
        # print("#################\n", request.form, "\n##############")
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
                                # print('--------->profile')
                                sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                                ), 'profile': list_profile[dem_profile]},  "service": j})
                                dem_profile += 1
                                set_mode = 1
                        except:
                            # print('else')
                            pass
                if (set_mode == 0):
                    sequen.append({"data": {"entity_id": i.split(
                        '(')[1].replace(')', '').strip()},  "service": j})
            elif j.find('delay') != -1:
                sequen.append({"delay": list_delay[dem_delay]})
                dem_delay += 1
            else:
                sequen.append({"data": {"entity_id": i.split(
                    '(')[1].replace(')', '').strip()},  "service": j})
        data = {"alias": request.form['ten'], "sequence": sequen}
        dict_[id] = data
        dict2yaml(dict_, file_path)
        # reload scripts
        secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
        url_service = '{}:8123/api/services/script/reload'.format(LOCAL_HOST)
        data = yaml2dict(secret_file)
        authen_code = data['token']
        headers = {
            "Authorization": "Bearer " + authen_code,
            "content-type": "application/json"
        }
        requests.post(url_service, headers=headers)
        return add_scripts_home()


@mod.route('/add_scripts_recall_edit', methods=['GET'])
def add_scripts_recall_edit():
    if request.method == 'GET':
        try:
            id_item = str(request.args.get('id_item'))
            file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
            dict_ = yaml2dict(file_path)
            secrets_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            data = yaml2dict(secrets_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            try:
                res_entity = requests.get(URL_STATE, headers=headers)
                list_entity = res_entity.json()
                entitys = []
                domains = []
                result_entity = []
                result_list_service = []
                for en in list_entity:
                    # print(en)
                    if "friendly_name" in en["attributes"].keys():
                        entitys.append(
                            en["attributes"]["friendly_name"].lower()+" (" + en['entity_id'] + ")")
                res_service = requests.get(URL_SERVICE, headers=headers)
                list_service = res_service.json()
                for ser in list_service:
                    for en in entitys:
                        if re.search(ser['domain'], en):
                            result_entity.append(en)

            except requests.exceptions.ConnectionError:
                result_entity = None
            result_entity.sort()
            scripts = []
            for i in dict_[id_item]['sequence']:
                add_name = 0
                try:
                    if (i['data'].get('volume_level') != None):
                        i['data']['volume_level'] = int(
                            i['data']['volume_level']*100)
                    for j in result_entity:
                        if (i['data']['entity_id'] == j.split('(')[1].split(')')[0]):
                            i['data']['entity_id'] = j
                            add_name = 1
                    if (add_name == 0):
                        i['data']['entity_id'] = ''
                except:
                    pass
                    # print('\n----------------\nit\'s delay\n--------------\n')
            len_dict_ = (len(dict_[id_item]['sequence'])-1)
            # print(dict_[id_item])
            # print(result_entity)
            return render_template('./scripts_manager/add_scripts_recall_edit.html', scripts=dict_[id_item], list_entitys=result_entity, len_dict=len_dict_, id_item=id_item)
        except Exception as error:
            # print("1: ", error)
            file_name = os.path.join(ROOT_DIR, 'scripts.yaml')
            try:
                list_scripts = yaml2dict(file_name)
            except Exception as error:
                # print("2: ", error)
                f = open(file_name, "w")
                list_scripts = yaml2dict(file_name)
                f.close()
            res_list = {}
            if list_scripts != None:
                if len(list_scripts) != 0:
                    for lists in list_scripts.keys():
                        if 'alias' in list_scripts[lists]:
                            if int(list_scripts[lists]['alias'].find('Báo nói')) == -1:
                                res_list[lists] = list_scripts[lists]

            return render_template('./scripts_manager/add_scripts_home.html', list_scripts=res_list, err='Kịch bản này không được sửa !')
    return render_template('./scripts_manager/add_scripts_recall_edit.html')


@mod.route('/add_scripts_recall_edit', methods=['POST'])
def edit_scripts_result():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            id_item = request.args.get('id_item')
            file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
            dict_ = yaml2dict(file_path)
            dict_.pop(id_item, None)
            idx = str(id_item)
            # print('-----------------\n', request.form, '\n-----------------')
            # print(idx, dict_)
            list_entity = request.form.getlist("entity")
            list_service = request.form.getlist("action")
            # print('-----------------\n list_entity\n-----------------\n',
            #   list_entity, '\n-----------------')
            # print('-----------------\n list_service\n-----------------\n',
            #   list_service, '\n-----------------')
            count_index = -1
            for i in list_service:
                count_index += 1
                # print(i)
                if i == 'delay':
                    list_entity.insert(count_index, 'delay')
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
            # cover
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
                # print('-----------------\ndel_action\n-----------------')
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
                                    # print('--------->profile')
                                    sequen.append({"data": {"entity_id": i.split('(')[1].replace(')', '').strip(
                                    ), 'profile': list_profile[dem_profile]},  "service": j})
                                    dem_profile += 1
                                    set_mode = 1
                            except:
                                pass
                                # print('else')
                    if (set_mode == 0):
                        sequen.append({"data": {"entity_id": i.split(
                            '(')[1].replace(')', '').strip()},  "service": j})
                elif j.find('delay') != -1:
                    sequen.append({"delay": list_delay[dem_delay]})
                    dem_delay += 1
                else:
                    sequen.append({"data": {"entity_id": i.split(
                        '(')[1].replace(')', '').strip()},  "service": j})

            data = {
                "alias": request.form['ten'], "sequence": sequen}
            dict_[idx] = data
            dict2yaml(dict_, file_path)
            # reload scripts
            secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            url_service = '{}:8123/api/services/script/reload'.format(
                LOCAL_HOST)
            data = yaml2dict(secret_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            requests.post(url_service, headers=headers)
            return add_scripts_home()


@mod.route('/add_scripts_recall_delete', methods=['GET'])
def delete_scripts():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
            dict_ = yaml2dict(file_path)
            id_ = str(request.args.get('id_item'))
            # print(id_)
            dict_.pop(id_, None)
            # print(dict_)
            dict2yaml(dict_, file_path)
            # reload scripts
            secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
            url_service = '{}:8123/api/services/script/reload'.format(
                LOCAL_HOST)
            data = yaml2dict(secret_file)
            authen_code = data['token']
            headers = {
                "Authorization": "Bearer " + authen_code,
                "content-type": "application/json"
            }
            requests.post(url_service, headers=headers)
            return add_scripts_home()
        return render_template('./login.html')
    return render_template('./login.html')
