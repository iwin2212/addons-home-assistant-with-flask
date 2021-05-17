from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
mod = Blueprint('sensor', __name__)

# thao tac voi sensor


@mod.route('/sensor')
def show_sensor():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            filename = os.path.join(ROOT_DIR, 'sensor.yaml')
            check_exist(filename)
            list_sensor = yaml2dict(filename)
            return render_template('./sensor/sensor.html', list_sensor=list_sensor, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_sensor')
def add_sensor():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            return render_template('./sensor/add_sensor.html')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_sensor', methods=['POST'])
def add_sensor_handler():
    filename = os.path.join(ROOT_DIR, 'sensor.yaml')
    check_exist(filename)
    list_sensor = yaml2dict(filename)
    if request.method == 'POST':
        list_sensor.append({
            "platform": "broadlink",
            "host": request.form['host'],
            "mac": request.form["mac"],
            "scan_interval": request.form['update_interval'],
            "monitored_conditions": [
                "temperature", "humidity", "air_quality", "noise", "light"
            ]
        })
    dict2yaml(list_sensor, filename)
    return show_sensor()
