from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
import json
from const import *
import os
import requests
import threading
import re
import socket
import time
from wifi_connector import *
from learn_command import learning_command_with_ir, learning_command_with_rf, learning_command_rf
mod = Blueprint('measure', __name__)


@mod.route('/e_measure')
def e_measure():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                info = request.args.get('info')
                note = request.args.get('note')
                # get name of device
                filename = os.path.join(ROOT_DIR, 'sensor.yaml')
                check_exist(filename)
                file_sensor = yaml2dict(filename)
                # print(file_sensor)
                measure_data = []
                for i in file_sensor:
                    try:
                        if i['unit_of_measurement'] == "V":
                            measure_data.append(i['state_topic'])
                    except:
                        pass
                # get quantity
                list_name = []
                for i in measure_data:
                    data = []
                    for j in file_sensor:
                        try:
                            if (j['state_topic'] == i):
                                data.append(j['name'])
                        except:
                            pass
                    list_name.append(data)
                return render_template('./e_measure/electric_measure.html', list_e=measure_data, list_name=list_name, info=info, note=note)
            except:
                measure_data = []
                list_name = []
                return render_template('./e_measure/electric_measure.html', list_e=measure_data, list_name=list_name, info=info, note=note)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_e_measure', methods=['GET', 'POST'])
def add_e_measure():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                return render_template('./e_measure/add_e_measure.html')
            else:
                # save to sensor.yaml
                ip = request.form['ip']
                url_service = 'http://' + ip + '/api/info'
                data = yaml2dict(secret_file)
                authen_code = data['token']
                headers = {
                    "Authorization": "Bearer " + authen_code,
                    "content-type": "application/json"
                }
                res = requests.post(url_service, headers=headers)
                data = res.json()
                id_dev = data['id']
                name_dev = data['name']

                filename = os.path.join(ROOT_DIR, 'sensor.yaml')
                file_sensor = yaml2dict(filename)
                if file_sensor == None:
                    file_sensor = []
                measure_data = []
                for i in file_sensor:
                    try:
                        if (i['state_topic'].find(str(id_dev)) != -1):
                            return e_measure()
                    except:
                        pass
                data_v = []
                if (request.form['type'] == 'jew'):
                    unit_dict = {}
                    unit_dict['Voltage'] = request.form['Voltage']
                    unit_dict['Power'] = request.form['Power']
                    unit_dict['Current'] = request.form['Current']
                    unit_dict['Today'] = request.form['Today']
                    unit_dict['Yesterday'] = request.form['Yesterday']
                    unit_dict['Thismonth'] = request.form['Thismonth']
                    unit_dict['Lastmonth'] = request.form['Lastmonth']

                    unit = ["V", "W", "A", "kWh",
                            "kWh", "kWh", "kWh"]
                    count = 0
                    for key, value in unit_dict.items():
                        data_v.append({
                            "platform": "mqtt",
                            "name": value,
                            "state_topic": name_dev.lower().replace(' ', '') + '/' + str(id_dev) + '/get/',
                            "value_template": '{{ value_json["Energy"].' + key + ' }}',
                            "unit_of_measurement": unit[count]
                        })
                        count += 1
                else:
                    unit_dict = {}
                    unit_dict['Voltage'] = request.form['Voltage']
                    unit_dict['Power'] = request.form['Power']
                    unit_dict['Current'] = request.form['Current']
                    unit_dict['Frequency'] = request.form['Frequency']
                    unit_dict['Factor'] = request.form['Factor']
                    unit_dict['Today'] = request.form['Today']
                    unit_dict['Yesterday'] = request.form['Yesterday']
                    unit_dict['Thismonth'] = request.form['Thismonth']
                    unit_dict['Lastmonth'] = request.form['Lastmonth']
                    unit_dict['Paymonth'] = request.form['Paymonth']
                    unit_dict['PayLastmonth'] = request.form['PayLastmonth']

                    unit = ["V", "W", "A", "Hz", "", "kWh",
                            "kWh", "kWh", "kWh", "VND", "VND"]
                    count = 0
                    for key, value in unit_dict.items():
                        data_v.append({
                            "platform": "mqtt",
                            "name": value,
                            "state_topic": name_dev.lower().replace(' ', '') + '/' + str(id_dev) + '/get/',
                            "value_template": '{{ value_json["Energy"].' + key + ' }}',
                            "unit_of_measurement": unit[count]
                        })
                        count += 1
                    for item in data_v:
                        try:
                            if item['unit_of_measurement'] == '':
                                item.pop("unit_of_measurement")
                        except:
                            pass
                sensor_data = yaml2dict(filename)
                dict2yaml(sensor_data + data_v, filename)
                # save to switch.yaml
                fileswitch = os.path.join(ROOT_DIR, 'switch.yaml')
                switch_data = yaml2dict(fileswitch)
                if switch_data == None:
                    switch_data = []
                data_s = []
                data_s.append({
                    'platform': 'mqtt',
                    'name': request.form['iden'],
                    'state_topic': str(id_dev) + "/electric.1/state",
                    'command_topic': str(id_dev) + "/electric.1/set",
                    'payload_on': "on",
                    'payload_off': "off",
                    'state_on': "on",
                    'state_off': "off",
                    'optimistic': False,
                    'qos': 0
                })
                dict2yaml(switch_data + data_s, fileswitch)
                return e_measure()
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/del_e', methods=['GET', 'POST'])
def del_e():
    if 'logged_in' in session:
        if session['logged_in']:
            dev = request.args.get('dev')
            filename = os.path.join(ROOT_DIR, 'sensor.yaml')
            file_sensor = yaml2dict(filename)
            measure_data = []
            for i in file_sensor:
                try:
                    if i['state_topic'] == dev:
                        pass
                    else:
                        measure_data.append(i)
                except:
                    measure_data.append(i)
            dict2yaml(measure_data, filename)

            fileswitch = os.path.join(ROOT_DIR, 'switch.yaml')
            file_switch = yaml2dict(fileswitch)
            switch_data = []
            if (dev.find('javispowermeter') != -1):
                dev = dev.split('javispowermeter/')[1].split('/get/')[0]
            for i in file_switch:
                try:
                    if i['state_topic'].find(dev) != -1:
                        pass
                    else:
                        switch_data.append(i)
                except:
                    switch_data.append(i)
            dict2yaml(switch_data, fileswitch)

            return e_measure()
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')
