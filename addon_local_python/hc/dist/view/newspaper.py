from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
mod = Blueprint('newspaper', __name__)


@mod.route('/newspaper', methods=['GET'])
def newspaper_home():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
            list_newspaper = {}
            try:
                list_scripts = yaml2dict(file_path)
            except Exception:

                f = open(file_path, 'w')
                list_scripts = yaml2dict(file_path)

                f.close
            if list_scripts != None:
                if len(list_scripts) != 0:
                    for lists in list_scripts.keys():
                        if int(list_scripts[lists]['alias'].find('Báo nói')) != -1:
                            list_newspaper[lists] = list_scripts[lists]
                            # print('Kes =========', list_scripts[lists]['alias'].find('Báo nói'))
                            # print(list_newspaper)

            return render_template('./newspaper/add_newspaper_home.html', list_scripts=list_newspaper)

        return render_template('./login.html')
    return render_template('./login.html')


@mod.route('/add_newspaper', methods=['GET'])
def add_newspaper():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            list_services = get_services()
            # print(list_services)
            index = 0
            err = ''
            for en in list_services:
                if en['domain'] == 'tts':
                    index += 1
                if en['domain'] == 'read_news':
                    index += 1
            # print(index)
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
                list_media = []
                res_service = requests.get(
                    URL_SERVICE, headers=headers)
                list_service = res_service.json()
                list_tts = []
                for entity in list_entity:
                    if entity['entity_id'].find('media') != -1:
                        list_media.append(
                            entity['entity_id'])
            except requests.exceptions.ConnectionError:
                list_media = None
                return render_template('./error/not_found.html')

            return render_template('./newspaper/add_newspaper.html', list_media=list_media, index=index)


@mod.route('/add_service_readnew', methods=['GET'])
def add_service_readnews():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            code = ''
            with open('read_news.py', 'r', encoding='utf-8') as f:
                code = f.read()
            # print(code)

            path_code = os.path.join(
                ROOT_DIR, 'custom_components/read_news.py')
            with open(path_code, 'w', encoding='utf-8') as file:
                file.write(code)
            try:
                subprocess.call(['sv', 'down', 'hass'])
                subprocess.call(['pkill', 'hass'])
                subprocess.call(['sv', 'up', 'hass'])
            except:
                secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
                url_service = 'http://localhost:8123/api/services/homeassistant/restart'
                data = yaml2dict(secret_file)
                authen_code = data['token']
                headers = {
                    "Authorization": "Bearer " + authen_code,
                    "content-type": "application/json"
                }
                res = requests.post(url_service, headers=headers)
            return newspaper_home()

        # return render_template('./login.html')
    # return render_template('./login.html')


@mod.route('/add_newspaper_result', methods=['GET', 'POST'])
def add_newspaper_result():
    if request.method == 'POST':

        file_path = os.path.join(ROOT_DIR, 'scripts.yaml')
        list_newspaper = {}
        list_scripts = {}
        try:
            list_scripts = yaml2dict(file_path)

        except Exception:
            # print("exception")
            f = open(file_path, 'w')
            list_scripts = yaml2dict(file_path)
            f.close
        if list_scripts != None:
            if len(list_scripts) != 0:
                for lists in list_scripts.keys():
                    if int(list_scripts[lists]['alias'].find('Báo nói')) != -1:
                        list_newspaper[lists] = list_scripts[lists]

        if list_scripts == None:
            list_scripts = {}
        if list_scripts != None:
            if len(list_scripts) == 0:
                list_scripts = {}
        id_ = str(int(time.time()))
        dau = 0
        if len(list_newspaper) != 0:
            for i in list_newspaper:
                if list_newspaper[i]['alias'].strip()[-1].isdigit():
                    dau = int(list_newspaper[i]['alias'].strip()[-1]) + 1
                    name_scripts = 'Báo nói ' + str(dau)
                else:
                    name_scripts = 'Báo nói 1'
        else:
            name_scripts = 'Báo nói 1'
        newsname = request.form['newsname']
        if newsname == 'Dân trí':
            newsname = 'dantri'
        elif newsname == 'Vietnamnet':
            newsname = 'vietnamnet'
        entity_id = request.form['entity_id']
        service = request.form['service'].strip()
        sequence = []
        sequence.append({'data': {'cache': 'false', 'news_name': newsname, 'entity_id': entity_id,
                                  'tts_service': 'tts.google_translate_say'}, 'service': service})
        list_scripts[id_] = {'alias': name_scripts, 'sequence': sequence}
        dict2yaml(list_scripts, file_path)
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
        return newspaper_home()


@mod.route('/newspaper_delete', methods=['GET', 'POST'])
def newspaper_delete():
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
            return newspaper_home()
        return render_template('./login.html')
    return render_template('./login.html')
