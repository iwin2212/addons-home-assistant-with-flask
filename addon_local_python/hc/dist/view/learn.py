from flask import render_template, request, session, jsonify, Blueprint
from yaml_util import yaml2dict
from utils import *
import time
from view.media import list_TV
from view.climate import climate_rm
from learn_command import learning_command_with_ir, learning_command_rf
mod = Blueprint('learn', __name__)


@mod.route('/hoc_lenh')
def hoc_lenh():
    if 'logged_in' in session:
        if session['logged_in']:
            list_broadlink, list_mac, list_host = broadlink_devices_info()
            return render_template('./media/hoc_lenh.html', list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host)
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/hoc_lenh', methods=['POST'])
def hoc_lenh_handle():
    model = request.form['model']
    manu = request.form['manufacture']
    data = {}
    data['commands'] = {}
    data["manufacturer"] = manu
    data['supportedModels'] = [model]
    data['supportedController'] = "Broadlink"
    data['commandsEncoding'] = "Base64"
    data['commands']['on'] = request.form['turn_on']
    data['commands']['off'] = request.form['turn_off']
    data['commands']['previousChannel'] = request.form['previous_channel']
    data['commands']['nextChannel'] = request.form['next_channel']
    data['commands']['volumeUp'] = request.form['volume_up']
    data['commands']['volumeDown'] = request.form['volume_down']
    data['commands']['mute'] = request.form['mute']
    data['commands']['sources'] = {}
    for i in range(10):
        data['commands']['sources']['Channel ' +
                                    str(i)] = request.form['channel' + str(i)]
    code = int(time.time())
    filename = str(code) + '.json'
    with open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player', filename), 'w') as outfile:
        json.dump(data, outfile, indent=4)

    IR_CODE = load_ircode()
    try:
        IR_CODE['media_player'][manu][model] = code
    except:
        IR_CODE['media_player'][manu] = {}
        IR_CODE['media_player'][manu][model] = code
    write_ircode(IR_CODE)
    return list_TV()


@mod.route('/hoc_lenh_dieu_hoa', methods=['GET', 'POST'])
def hoc_lenh_dieu_hoa():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                list_broadlink, list_mac, list_host = broadlink_devices_info()
                return render_template('./air_condition/climate_remote.html', list_broadlink=list_broadlink, success='', list_mac=list_mac, list_host=list_host)
            else:
                model = request.form['model']
                manu = request.form['manufacture']
                IR_CODE = load_ircode()
                if manu in IR_CODE["climate"]:
                    if model in IR_CODE["climate"][manu]:
                        code = IR_CODE["climate"][manu][model]
                    else:
                        code = int(time.time())
                else:
                    code = int(time.time())
                op_mode = request.form["operation_mode"].lower()
                fan_mode = request.form["fan_mode"].lower()

                filename = str(code) + '.json'
                fullpath_filename = os.path.join(
                    ROOT_DIR, 'custom_components/smartir/codes/climate', filename)
                data = {}
                data['commands'] = {}
                data["manufacturer"] = manu
                data['supportedModels'] = [model]
                data['supportedController'] = "Broadlink"
                data['commandsEncoding'] = "Base64"
                data['minTemperature'] = 18.0
                data['maxTemperature'] = 30.0
                data['precision'] = 1.0
                data["operationModes"] = ["cool", "heat", "off"]
                data["fanModes"] = ["low", "mid", "high", "auto"]
                data['commands']['off'] = request.form['buttonoff']
                data['commands']['cool'] = {}
                data['commands']['heat'] = {}
                data['commands']['cool']['auto'] = {}
                data['commands']['cool']['low'] = {}
                data['commands']['cool']['mid'] = {}
                data['commands']['cool']['high'] = {}
                data['commands']['heat']['auto'] = {}
                data['commands']['heat']['low'] = {}
                data['commands']['heat']['mid'] = {}
                data['commands']['heat']['high'] = {}
                for i in range(18, 31):
                    data['commands']['cool']['auto'][str(
                        i)] = request.form["button" + str(i)]

                for i in range(31, 44):
                    data['commands']['cool']['low'][str(
                        i-13*1)] = request.form["button" + str(i)]

                for i in range(44, 57):
                    data['commands']['cool']['mid'][str(
                        i-13*2)] = request.form["button" + str(i)]

                for i in range(57, 70):
                    data['commands']['cool']['high'][str(
                        i-13*3)] = request.form["button" + str(i)]

                for i in range(70, 83):
                    data['commands']['heat']['auto'][str(
                        i-13*4)] = request.form["button" + str(i)]

                for i in range(83, 96):
                    data['commands']['heat']['low'][str(
                        i-13*5)] = request.form["button" + str(i)]

                for i in range(96, 109):
                    data['commands']['heat']['mid'][str(
                        i-13*6)] = request.form["button" + str(i)]

                for i in range(109, 122):
                    data['commands']['heat']['high'][str(
                        i-13*7)] = request.form["button" + str(i)]
                # print("Tạo file mới")
                # print(data)
                # except Exception:
                #         print("Lỗi thêm điều khiển")

                with open(fullpath_filename, 'w') as outfile:
                    json.dump(data, outfile, indent=4)
                # print("Dumpedddd file")
                try:
                    IR_CODE['climate'][manu][model] = code
                except:
                    IR_CODE['climate'][manu] = {}
                    IR_CODE['climate'][manu][model] = code
                write_ircode(IR_CODE)
                list_broadlink = yaml2dict(
                    os.path.join(ROOT_DIR, 'switch.yaml'))
                return climate_rm()
        else:
            return render_template('./login.html', error='')
    else:
        return render_template('./login.html', error='')


@mod.route('/learn_command', methods=['POST'])
def command_handle():
    entity_id = request.args.get('entity_id')
    
    p = learning_command_with_ir(entity_id)
    return jsonify(result=p)


@mod.route('/learn_command_rf', methods=['POST'])
def command_handling():
    entity_id = request.args.get('entity_id')
    p = learning_command_rf(entity_id)
    return jsonify(result=p)
