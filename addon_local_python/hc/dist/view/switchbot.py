from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('switchbot', __name__)


@mod.route('/switchbot')
def switchbot():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            switch_file = os.path.join(ROOT_DIR, 'switch.yaml')
            switch_data = yaml2dict(switch_file)
            list_switchbot = [i for i in switch_data if (
                i['platform'] == 'switchbot')]
            return render_template('./switchbot/switchbot.html', list_switchbot=list_switchbot, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/delete_switchbot',  methods=['GET', 'POST'])
def delete_switchbot():
    mac = request.args.get('mac')
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    data = yaml2dict(filename)
    for i in range(len(data)):
        try:
            if (data[i]['mac'] == mac):
                del data[i]
        except:
            pass
    dict2yaml(data, filename)
    return switchbot()


@mod.route('/add_switchbot', methods=['GET', 'POST'])
def add_switchbot():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                switch_file = os.path.join(ROOT_DIR, 'switch.yaml')
                switch_data = yaml2dict(switch_file)
                list_mac = [i['mac'] for i in switch_data if (
                    i['platform'] == 'switchbot')]
                return render_template('./switchbot/add_switchbot.html', list_mac=list_mac)
            else:
                filename = os.path.join(ROOT_DIR, 'switch.yaml')
                data = yaml2dict(filename)
                data.append({
                    "mac": request.form['mac'].strip(),
                    "platform": "switchbot",
                    "name": request.form['name']
                })
                dict2yaml(data, filename)
                return switchbot()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')
