from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('fan', __name__)


# thao tac voi fan
@mod.route('/fan')
def show_fan():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công. "
            fan_file = os.path.join(ROOT_DIR, 'fan.yaml')
            check_exist(fan_file)
            list_fan = yaml2dict(fan_file)
            list_entity_id = get_list_entity_id()
            return render_template('./fan/fan.html', list_fan=list_fan, info=info, list_entity_id=list_entity_id)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_fan', methods=['GET', 'POST'])
def add_fan():
    if request.method == 'GET':
        if 'logged_in' in session:
            if session['logged_in'] == True:
                list_broadlink, list_mac, list_host = broadlink_devices_info()
                IR_CODE = load_ircode()
                list_ir = IR_CODE['fan']
                return render_template('./fan/add_fan.html', list_broadlink=list_broadlink, list_ir=list_ir, list_mac=list_mac, list_host=list_host)
            return render_template('./login.html', error='')
        return render_template('./login.html', error='')
    elif request.method == 'POST':
        filename = os.path.join(ROOT_DIR, 'fan.yaml')
        data = dict()
        data['name'] = request.form['name']
        data['controller_data'] = request.form['gateway']
        data['unique_id'] = no_accent_vietnamese(
            request.form["name"]).lower().replace(" ", "_") + str(int(time.time()))
        device_code = int(request.form["device_code"].split("(")[-1][:-1])
        data['device_code'] = device_code
        data['platform'] = 'smartir'
        check_exist(filename)
        dict_ = yaml2dict(filename)
        dict_.append(data)
        dict2yaml(dict_, filename)
        return show_fan()


@mod.route('/list_fan')
def list_fan():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            f = open(os.path.join(data_file, 'ircode.json'))
            IR_CODE = json.load(f)
            f.close()
            list_model = IR_CODE['fan']
            return render_template('./fan/list_fan.html', list_fan=list_model)
        else:
            return render_template('./login.html', err='')
    else:
        return render_template('./login.html', err='')


@mod.route('/fan_remote', methods=['GET', "POST"])
def fan_remote():
    if 'logged_in' in session:
        if session['logged_in']:
            fan = request.args.get('fan')
            code = request.args.get('code')
            model = request.args.get('model')
            if request.method == "GET":
                # load các file trong model
                try:
                    filename = os.path.join(
                        ROOT_DIR, 'custom_components/smartir/codes/fan', code + '.json')
                    f = open(filename, 'r')
                    data = json.load(f)
                    f.close()
                    list_switch = yaml2dict(
                        os.path.join(ROOT_DIR, 'switch.yaml'))
                    list_gateway = [
                        i for i in list_switch if i['platform'] == 'broadlink']
                    list_button = {}
                    list_button["numspeed"] = len(data["commands"]['default'])
                    list_button["off"] = data["commands"]["off"]
                    list_speed = []
                    for key, value in data["commands"]['default'].items():
                        list_speed.append(value)
                    # print("______________________", list_speed)
                    return render_template('./fan/fan_remote.html', fan=fan, code=code, list_gateway=list_gateway, model=model, list_button=list_button, list_speed=list_speed)
                except:
                    return "Không sửa được code của MODEL này, vui lòng quay lại"
            else:
                model = request.form['model']
                manu = request.form['manufacture']
                data = {}
                data['commands'] = {}
                data["manufacturer"] = [manu]
                data['supportedModels'] = model
                data['supportedController'] = "Broadlink"
                data['commandsEncoding'] = "Base64"
                data['commands']['off'] = request.form['turn_on']
                data['commands']['default'] = {}
                num_of_speed = int(request.form['numspeed'])
                switcher = {
                    1: ["low"],
                    2: ["low", "high"],
                    3: ["low", "medium", "high"],
                    4: ["lowest", "low", "medium", "high"],
                    5: ["lowest", "low", "medium", "high", "very high"],
                    6: ["lowest", "low", "mediumlow", "medium", "mediumhigh", "high"]
                }
                list_speed = switcher.get(num_of_speed)
                data["speed"] = list_speed[:num_of_speed]
                for i in range(num_of_speed):
                    data["commands"]['default'][list_speed[i]
                                                ] = request.form["button"+str(i+1)]
                # code = int(time.time())
                filename = code + '.json'
                filename = os.path.join(
                    ROOT_DIR, 'custom_components/smartir/codes/fan', code + '.json')

                with open(filename, 'w') as outfile:
                    json.dump(data, outfile, indent=4)

                IR_CODE = load_ircode()
                try:
                    IR_CODE['fan'][manu][model] = code
                except:
                    IR_CODE['fan'][manu] = {}
                    IR_CODE['fan'][manu][model] = code
                write_ircode(IR_CODE)
                return list_fan()
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/delete_fan', methods=['POST'])
def delete_fan():
    iden = request.args.get('iden')
    list_fan = yaml2dict(os.path.join(ROOT_DIR, 'fan.yaml'))
    list_fan = [i for i in list_fan if i['unique_id'] != iden]
    dict2yaml(list_fan, os.path.join(ROOT_DIR, 'fan.yaml'))
    return show_fan()


@mod.route('/check_command_fan_off', methods=['POST'])
def check_command_fan_off():
    mac = request.args.get('mac')
    host = request.args.get('host')
    model = request.args.get('model')
    model = model + '.json'
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/fan/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        fan_off = data['commands']['off']
        sending_ir_packet(mac, host, fan_off)
    return jsonify()


@mod.route('/check_command_fan_low', methods=['POST'])
def check_command_fan_low():
    mac = request.args.get('mac')
    host = request.args.get('host')
    model = request.args.get('model')
    model = model + '.json'
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/fan/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        fan_low = data['commands']['default']['low']
        sending_ir_packet(mac, host, fan_low)
    return jsonify()


@mod.route('/check_command_fan_medium', methods=['POST'])
def check_command_fan_medium():
    mac = request.args.get('mac')
    host = request.args.get('host')
    model = request.args.get('model')
    model = model + '.json'
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/fan/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        fan_medium = data['commands']['default']['medium']
        sending_ir_packet(mac, host, fan_medium)
    return jsonify()


@mod.route('/check_command_fan_high', methods=['POST'])
def check_command_fan_high():
    mac = request.args.get('mac')
    host = request.args.get('host')
    model = request.args.get('model')
    model = model + '.json'
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/fan/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        fan_high = data['commands']['default']['high']
        sending_ir_packet(mac, host, fan_high)
    return jsonify()


@mod.route('/hoc_lenh_fan', methods=['GET', 'POST'])
def hoc_lenh_fan():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == "GET":
                list_broadlink, list_mac, list_host = broadlink_devices_info()
                return render_template('./fan/hoc_lenh_fan.html', list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host)
            else:
                model = request.form['model']
                manu = request.form['manufacture']
                data = {}
                data['commands'] = {}
                data["manufacturer"] = [manu]
                data['supportedModels'] = model
                data['supportedController'] = "Broadlink"
                data['commandsEncoding'] = "Base64"
                data['commands']['off'] = request.form['turn_on']
                data['commands']['default'] = {}
                num_of_speed = int(request.form['numspeed'])
                switcher = {
                    1: ["low"],
                    2: ["low", "high"],
                    3: ["low", "medium", "high"],
                    4: ["lowest", "low", "medium", "high"],
                    5: ["lowest", "low", "medium", "high", "very high"],
                    6: ["lowest", "low", "mediumlow", "medium", "mediumhigh", "high"]
                }
                list_speed = switcher.get(num_of_speed)
                data["speed"] = list_speed[:num_of_speed]
                for i in range(num_of_speed):
                    data["commands"]['default'][list_speed[i]
                                                ] = request.form["button"+str(i+1)]

                code = int(time.time())
                filename = str(code) + '.json'
                with open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/fan', filename), 'w') as outfile:
                    json.dump(data, outfile, indent=4)

                IR_CODE = load_ircode()
                try:
                    IR_CODE['fan'][manu][model] = code
                except:
                    IR_CODE['fan'][manu] = {}
                    IR_CODE['fan'][manu][model] = code
                write_ircode(IR_CODE)
                return list_fan()


@mod.route('/hoc_lenh_fan_rf', methods=['GET', 'POST'])
def hoc_lenh_fan_rf():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == "GET":
                list_broadlink, list_mac, list_host = broadlink_devices_info()
                return render_template('./fan/hoc_lenh_fan_rf.html', list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host)
            else:
                model = request.form['model']
                manu = request.form['manufacture']
                data = {}
                data['commands'] = {}
                data["manufacturer"] = [manu]
                data['supportedModels'] = model
                data['supportedController'] = "Broadlink"
                data['commandsEncoding'] = "Base64"
                data['commands']['off'] = request.form['turn_on']
                data['commands']['default'] = {}
                num_of_speed = int(request.form['numspeed'])
                switcher = {
                    1: ["low"],
                    2: ["low", "high"],
                    3: ["low", "medium", "high"],
                    4: ["lowest", "low", "medium", "high"],
                    5: ["lowest", "low", "medium", "high", "very high"],
                    6: ["lowest", "low", "mediumlow", "medium", "mediumhigh", "high"]
                }
                list_speed = switcher.get(num_of_speed)
                data["speed"] = list_speed[:num_of_speed]
                for i in range(num_of_speed):
                    data["commands"]['default'][list_speed[i]
                                                ] = request.form["button"+str(i+1)]

                code = int(time.time())
                filename = str(code) + '.json'
                with open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/fan', filename), 'w') as outfile:
                    json.dump(data, outfile, indent=4)

                IR_CODE = load_ircode()
                try:
                    IR_CODE['fan'][manu][model] = str(code)
                except:
                    IR_CODE['fan'][manu] = {}
                    IR_CODE['fan'][manu][model] = str(code)
                write_ircode(IR_CODE)
                return list_fan()
