from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('climate', __name__)


@mod.route("/climate_rm")
def climate_rm():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            f = open(os.path.join(data_file, 'ircode.json'))
            IR_CODE = json.load(f)
            f.close()
            list_model = IR_CODE['climate']

            key_list = []
            for key in list_model:
                key_list.append(key.lower())
            key_list = sorted(key_list)

            model_sorted = {}
            for i in range(len(key_list)):
                for key in list_model:
                    if (key_list[i] == key.lower()):
                        model_sorted[key] = list_model[key]
            return render_template('./air_condition/climate_rm.html', list_model=model_sorted)
        else:
            return render_template('./login.html', err='')
    else:
        return render_template('./login.html', err='')


@mod.route("/climate_rm", methods=["POST"])
def delete_climate_rm():
    if 'logged_in' in session:
        if session["logged_in"]:
            if request.method == "POST":
                code = request.args.get('code')
                f = open(os.path.join(data_file, 'ircode.json'))
                IR_CODE = json.load(f)
                f.close()
                os.remove(os.path.join(
                    ROOT_DIR, 'custom_components/smartir/codes/climate', code + '.json'))
                for i in IR_CODE["climate"]:
                    for j in IR_CODE["climate"][i]:
                        if IR_CODE["climate"][i][j] == int(code):
                            vendor = i
                            model = j
                            break
                del IR_CODE["climate"][vendor][model]
                if IR_CODE["climate"][vendor] == {}:
                    del IR_CODE["climate"][vendor]
                with open(os.path.join(data_file, 'ircode.json'), 'w') as outfile:
                    json.dump(IR_CODE, outfile, indent=4)
                # print("ROOT_DIR =", ROOT_DIR)
                # print("Filename =", os.path.join(ROOT_DIR, 'custom_components/smartir/codes/climate', code + '.json'))
                return climate_rm()


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
                data["operationModes"] = ["cool", "heat"]
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
