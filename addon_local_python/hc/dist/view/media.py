from flask import Flask, render_template, request, redirect, session, jsonify, send_file, Blueprint
import os

from requests import models
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
mod = Blueprint('media', __name__)

# thao tac voi media


@mod.route('/media_player')
def show_media_player():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công. "
            filename = os.path.join(ROOT_DIR, 'media_player.yaml')
            check_exist(filename)
            list_media_player = yaml2dict(filename)
            return render_template('./media/media_player.html', list_media_player=list_media_player, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_media_player')
def add_media_player_device():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            list_gateway = get_broadlink_device_from_api()
            IR_CODE = load_ircode()
            list_ir = IR_CODE['media_player']
            # print(list_ir)
            list_ir = {k: v for k, v in sorted(list_ir.items())}
            # print(list_ir)
            return render_template('./media/add_media_player.html', list_gateway=list_gateway, list_ir=list_ir)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_media_player', methods=['POST'])
def add_media_player_result():
    if request.method == 'POST':
        filename = os.path.join(ROOT_DIR, 'media_player.yaml')
        data = dict()
        data['platform'] = 'smartir'
        data['name'] = request.form['name']
        data['controller_data'] = request.form['gateway']
        data['unique_id'] = no_accent_vietnamese(
            request.form["name"]).lower().replace(" ", "_") + str(int(time.time()))
        code = int(request.form["device_code"].split("(")[-1][:-1])
        device_code = int(time.time())
        try:
            g = open(os.path.join(
                ROOT_DIR, 'custom_components/smartir/codes/media_player/', str(code) + '.json'), 'r')
            org_data = json.load(g)
            g.close()
            f = open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player/',
                                  str(code) + str(device_code) + '.json'), 'w')
            json.dump(org_data, f, indent=4)
            g.close()
            f.close()
        except:
            g = open(os.path.join('data/template_media_ir.json'), 'r')
            org_data = json.load(g)
            g.close()
            f = open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player/',
                                  str(code) + str(device_code) + '.json'), 'w')
            json.dump(org_data, f, indent=4)
            f.close()
        data['device_code'] = str(code) + str(device_code)
        check_exist(filename)
        dict_ = yaml2dict(filename)
        dict_.append(data)
        dict2yaml(dict_, filename)

        # copy file json cua hang sang file khac cua tv
        return show_media_player()


@mod.route('/check_command_media_off', methods=['POST'])
def media_off():
    gateway = request.args.get('gateway')
    model = request.args.get('model')
    mac, ip = from_entity_id_get_mac_ip(gateway)
    model = model + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/media_player/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        off_cmd = data['commands']['off']
        sending_ir_packet(mac, ip, off_cmd)
    return jsonify()


@mod.route('/check_command_media_on', methods=['POST'])
def media_on():
    gateway = request.args.get('gateway')
    model = request.args.get('model')
    mac, ip = from_entity_id_get_mac_ip(gateway)
    model = model + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/media_player/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        on_cmd = data['commands']['on']
        sending_ir_packet(mac, ip, on_cmd)
    return jsonify()


@mod.route('/check_command_media_volume_up', methods=['POST'])
def media_volume_up():
    gateway = request.args.get('gateway')
    model = request.args.get('model')
    mac, ip = from_entity_id_get_mac_ip(gateway)
    model = model + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/media_player/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        volumeUp = data['commands']['volumeUp']
        sending_ir_packet(mac, ip, volumeUp)
    return jsonify()


@mod.route('/check_command_media_volume_down', methods=['POST'])
def media_volume_down():
    gateway = request.args.get('gateway')
    model = request.args.get('model')
    mac, ip = from_entity_id_get_mac_ip(gateway)
    model = model + '.json'

    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/codes/media_player/', model)

    with open(filedir) as json_file:
        data = json.load(json_file)
        volumeDown = data['commands']['volumeDown']
        sending_ir_packet(mac, ip, volumeDown)
    return jsonify()


@mod.route('/add_tv_channel')
def add_tv_channel_interface():
    if 'logged_in' in session:
        if session['logged_in']:
            unique_id = request.args.get('unique_id')
            error = ''
            list_tv = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
            for i in list_tv:
                if i['unique_id'] == unique_id:
                    TV = i
                    break
            return render_template('./media/add_tv_channel.html', error=error, TV=TV)
        else:
            return render_template('./login.html')
    return render_template('./login.html')


@mod.route('/add_tv_channel', methods=['POST'])
def add_tv_channel_handler():
    unique_id = request.args.get('unique_id')
    channel = request.form['channel']
    code = request.form['code']
    list_tv = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
    for tv in list_tv:
        if tv['unique_id'] == unique_id:
            filename = str(tv['device_code']) + '.json'
            break
    try:
        k = request.form["YES"]
    except:
        k = 'no'
    if k == "YES":
        result = get_new_channel(os.path.join(
            ROOT_DIR, 'custom_components/smartir/codes/media_player/', filename), "_" + channel, code)
    else:
        result = get_new_channel(os.path.join(
            ROOT_DIR, 'custom_components/smartir/codes/media_player/', filename), channel, code)
    if result == True:
        error = ''
        return render_template('./media/add_tv_channel.html', error=error, TV=tv)
    else:
        error = "Không có mã kênh thoả mãn"
        return render_template('./add_tv_channel.html', error=error, TV=tv)


@mod.route('/delete_TV', methods=['POST'])
def del_TV():
    iden = request.args.get('iden')
    list_TV = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
    list_TV = [i for i in list_TV if not (i['unique_id'] == iden)]
    dict2yaml(list_TV, os.path.join(ROOT_DIR, 'media_player.yaml'))

    return show_media_player()


@mod.route('/TV_control')
def TV_control():
    if 'logged_in' in session:
        if session['logged_in']:
            iden = request.args.get('iden')
            list_TV = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
            for TV_show in list_TV:
                if TV_show['unique_id'] == iden:
                    tv = TV_show
                    break
            f = open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player',
                                  str(tv['device_code']) + '.json'), 'r')
            data = json.load(f)
            final_list_channel = []
            list_channel = read_list_channel()
            for i in list_channel:
                final_list_channel.append([i[0], i[1], i[2][:-1], "", 0])
            count = len(list_channel) + 1
            for i in data['commands']['sources']:
                if type(data['commands']['sources'][i]) == list:

                    checked_in = check_in(list_channel, 1, i.upper())

                    if not checked_in[0]:
                        if i[0] == "_":
                            final_list_channel.append([str(count), i[1:].upper(), i[1:].upper(), list_command_2_string(
                                data['commands']['sources'][i], data['commands']['sources']), 1])
                            count += 1
                        else:
                            final_list_channel.append([str(count), i.upper(), i.upper(), list_command_2_string(
                                data['commands']['sources'][i], data['commands']['sources']), 0])
                            count += 1
                    else:
                        index = checked_in[1]
                        if i[0] == "_":
                            final_list_channel[index] = [str(index + 1), i[1:], list_channel[index][2], list_command_2_string(
                                data['commands']['sources'][i], data['commands']['sources']), 1]
                        else:
                            final_list_channel[index] = [str(index + 1), i, list_channel[index][2], list_command_2_string(
                                data['commands']['sources'][i], data['commands']['sources']), 0]

            return render_template('./media/TV_control_ver2.html', TV=tv, list_channel=final_list_channel)


@mod.route('/save_channel', methods=['POST'])
def save_channel():
    model = request.args.get('model')
    channel_name = request.args.get('channel_name')
    list_TV = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
    for i in list_TV:
        if i['unique_id'] == model:
            filename = str(i['device_code']) + '.json'
    try:
        if request.form['favorite'] == 'YES':
            # print("truong hop kenh yeu thich")
            get_new_channel(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player',
                                         filename), "_" + channel_name, request.form['code'])
        else:
            # print("khong yeu thich")
            get_new_channel(os.path.join(
                ROOT_DIR, 'custom_components/smartir/codes/media_player', filename), channel_name, request.form['code'])
    except:
        get_new_channel(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player',
                                     filename), channel_name, request.form['code'])

    return redirect('./TV_control/' + model)


@mod.route('/delete_channel', methods=['POST'])
def delete_channel():
    model = request.args.get('model')
    channel_name = request.args.get('channel_name')
    list_tv = yaml2dict(os.path.join(ROOT_DIR, 'media_player.yaml'))
    for tv in list_tv:
        if tv['unique_id'] == model:
            filename = str(tv['device_code']) + '.json'
    f = open(os.path.join(
        ROOT_DIR, 'custom_components/smartir/codes/media_player', filename), 'r')
    data = json.load(f)
    f.close()
    try:
        del data['commands']['sources'][channel_name]
    except:
        del data['commands']['sources']["_" + channel_name]
    with open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player', filename), 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return redirect('./TV_control/' + model)


@mod.route('/TV_remote')
def list_TV():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            f = open(os.path.join(data_file, 'ircode.json'))
            IR_CODE = json.load(f)
            f.close()
            list_model_tv = IR_CODE['media_player']
            return render_template('./media/tv_list.html', list_tv=list_model_tv)
        else:
            return render_template('./login.html', err='')
    else:
        return render_template('./login.html', err='')


@mod.route('/TV_remote')
def remote_tv():
    if 'logged_in' in session:
        if session['logged_in']:
            tv = request.args.get('tv')
            model = request.args.get('model')
            filename = os.path.join(
                ROOT_DIR, 'custom_components/smartir/codes/media_player', model + '.json')
            try:
                f = open(filename, 'r')
                data = json.load(f)
                f.close()
                list_channel = dict()
                for i in data['commands']:
                    if i != 'sources':
                        list_channel[i] = data['commands'][i]
                list_channel['sources'] = {}
                for i in data['commands']['sources']:
                    if i.lower().find("channel") != -1:
                        list_channel['sources'][i] = data['commands']['sources'][i]
                # print(list_channel)
                list_switch = yaml2dict(os.path.join(ROOT_DIR, 'switch.yaml'))
                list_broadlink, list_mac, list_host = broadlink_devices_info()
                return render_template('./media/tv_remote.html', tv=tv, model=model, list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host, list_channel=list_channel)
            except:
                return "File IR của model không tồn tại"
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/TV_remote', methods=['POST'])
def tv_remote_handle():
    model = request.args.get('model')
    filename = os.path.join(
        ROOT_DIR, 'custom_components/smartir/codes/media_player', model + '.json')
    f = open(filename, 'r')
    data = json.load(f)
    f.close()
    data['commands']['on'] = request.form['turn_on']
    data['commands']['off'] = request.form['turn_off']
    data['commands']['previousChannel'] = request.form['previous_channel']
    data['commands']['nextChannel'] = request.form['next_channel']
    data['commands']['volumeUp'] = request.form['volume_up']
    data['commands']['volumeDown'] = request.form['volume_down']
    data['commands']['mute'] = request.form['mute']
    for i in range(10):
        data['commands']['sources']['Channel ' +
                                    str(i)] = request.form['channel' + str(i)]
    with open(os.path.join(ROOT_DIR, 'custom_components/smartir/codes/media_player', filename), 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return list_TV()


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


@mod.route('/hoc_lenh')
def hoc_lenh():
    if 'logged_in' in session:
        if session['logged_in']:
            list_broadlink, list_mac, list_host = broadlink_devices_info()
            return render_template('./media/hoc_lenh.html', list_broadlink=list_broadlink, list_mac=list_mac, list_host=list_host)
        else:
            return render_template('./login.html', error='')
    return render_template('./login.html', error='')
