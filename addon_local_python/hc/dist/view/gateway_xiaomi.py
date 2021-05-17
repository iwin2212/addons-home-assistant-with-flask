from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
from token_extractor import get_token
mod = Blueprint('gateway_xiaomi', __name__)


@mod.route('/xiaomi_aqara')
def show_xiaomi_aqara():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                result = request.args.get('result')
                list_xiaomi = get_list_via_integration(
                    'xiaomi_aqara', 'xiaomi_miio')
                list_xiaomi_aqara = [i for i in list_xiaomi if (
                    i['entity_id'].split('.')[0] == 'light')]
                return render_template('gateway/xiaomi_aqara.html', list_xiaomi_aqara=list_xiaomi_aqara, result=result)
            except Exception as err:
                print(err)
                return render_template(
                    'index.html', error='Kết nối đến HA bị lỗi. Vui lòng thử lại sau')
    return render_template('login.html', error='')


@mod.route('/add_xiaomi_aqara')
def add_xiaomi_aqara():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            return render_template('gateway/add_xiaomi_aqara.html')
        return render_template('login.html', error='')
    return render_template('login.html', error='')


@mod.route('/config_aqara', methods=['POST'])
def config_aqara():
    username = request.args.get('username')
    password = request.args.get('password')
    result = get_token(username, password)
    return jsonify(result=result)


@mod.route('/connect_xiaomi', methods=['POST'])
def connect_xiaomi():
    token = request.args.get('token')
    ip = request.args.get('ip')
    name = request.args.get('name')
    result = config_integration_xiaomi('xiaomi_miio', token, ip, name)
    return jsonify(result=result)


@mod.route('/delete_xiaomi', methods=['POST'])
def delete_xiaomi_aqara():
    entity_id = request.args.get('id')
    result = delete_entity_via_integration('xiaomi_aqara', entity_id)
    return show_xiaomi_aqara()
