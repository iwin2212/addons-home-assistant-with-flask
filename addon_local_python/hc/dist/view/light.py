from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('light', __name__)


# light domain
@mod.route('/light')
def show_light():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                result = request.args.get('result')
                list_yeelight = get_list_via_integration('yeelight')
                return render_template('./light/light.html', list_yeelight=list_yeelight, result=result)
            except:
                return render_template(
                    'index.html', error='Kết nối đến HA bị lỗi. Vui lòng thử lại sau')
    return render_template('./login.html', error='')


@mod.route('/add_light')
def add_light():
    if 'logged_in' in session:
        if session['logged_in']:
            return render_template('./light/add_light.html')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/config_yeelight', methods=['GET', 'POST'])
def add_light_handler():
    host = request.args.get('host')
    result = config_integration_device('yeelight', '', host, '')
    return jsonify(result)


@mod.route('/delete_light', methods=['POST'])
def rm_light():
    entity_id = request.args.get('id')
    result = delete_entity_via_integration('yeelight', entity_id)
    return show_light()
