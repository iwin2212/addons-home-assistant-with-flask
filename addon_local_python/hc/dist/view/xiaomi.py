from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('xiaomi', __name__)


@mod.route('/xiaomi_switch')
def xiaomi_switch():
    if 'logged_in' in session:
        if session['logged_in']:
            list_broadlink = yaml2dict(os.path.join(ROOT_DIR, 'switch.yaml'))
            list_xiaomi_switch = [
                i for i in list_broadlink if i['platform'] == 'xiaomi_miio']
            return render_template('./xiaomi_switch/xiaomi_switch.html', list_xiaomi_switch=list_xiaomi_switch)
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/delete_xiaomi_switch', methods=['POST'])
def delete_xiaomi_switch():
    device_token = request.args.get('device_token')
    filename = os.path.join(ROOT_DIR, 'switch.yaml')
    list_switch = yaml2dict(filename)
    list_xiaomi_switch = [
        i for i in list_switch if i['platform'] == 'xiaomi_miio']
    list_switch_without_xiaomi = [
        i for i in list_switch if i['platform'] != 'xiaomi_miio']
    list_xiaomi_switch_final = [
        i for i in list_xiaomi_switch if i['token'] != device_token]
    list_switch_final = list_switch_without_xiaomi + list_xiaomi_switch_final
    dict2yaml(list_switch_final, filename)
    return xiaomi_switch()


@mod.route('/add_xiaomi_switch', methods=['GET', 'POST'])
def add_xiaomi_switch():
    if request.method == 'GET':
        return render_template('./xiaomi_switch/add_xiaomi_switch.html')
    else:
        data = {
            "platform": "xiaomi_miio",
            "host": request.form['host'],
            "name": request.form['name'],
            "token": request.form['token'],
            "model": request.form['model']
        }
        filename = os.path.join(ROOT_DIR, 'switch.yaml')
        list_switch = yaml2dict(filename)
        list_switch.append(data)
        dict2yaml(list_switch, filename)
        return xiaomi_switch()


@mod.route('/xiaomi_robot')
def xiaomi_robot():
    if 'logged_in' in session:
        if session['logged_in']:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            check_exist(os.path.join(ROOT_DIR, 'vacuum.yaml'))
            list_vacuum = yaml2dict(os.path.join(ROOT_DIR, 'vacuum.yaml'))
            return render_template('./xiaomi_robot/xiaomi_robot.html', list_xiaomi_robot=list_vacuum, info=info)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/add_xiaomi_robot', methods=['GET', 'POST'])
def add_xiaomi_robot():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                return render_template('./xiaomi_robot/add_xiaomi_robot.html')
            else:
                data = {
                    "platform": "xiaomi_miio",
                    "host": request.form["host"],
                    "token": request.form["token"],
                    "name": request.form["name"]
                }
                vacuum_list = yaml2dict(os.path.join(ROOT_DIR, 'vacuum.yaml'))
                vacuum_list.append(data)
                dict2yaml(vacuum_list, os.path.join(ROOT_DIR, 'vacuum.yaml'))
                return xiaomi_robot()


@mod.route('/delete_xiaomi_robot', methods=['POST'])
def delete_xiaomi_robot():
    device_token = request.args.get('device_token')
    list_vacuum = yaml2dict(os.path.join(ROOT_DIR, 'vacuum.yaml'))
    list_vacuum = [i for i in list_vacuum if i['token'] != device_token]
    dict2yaml(list_vacuum, os.path.join(ROOT_DIR, 'vacuum.yaml'))
    return render_template('./xiaomi_robot/xiaomi_robot.html', list_xiaomi_robot=list_vacuum)
