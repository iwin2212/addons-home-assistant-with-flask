from flask import render_template, request, session, jsonify, Blueprint
from utils import *
from const import *
import os
from wifi_connector import *
mod = Blueprint('wifi', __name__)


@mod.route('/wifi', methods=['GET', 'POST'])
def wifi():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                # wifi networks available to connect:
                wifi_list, signal_list, security_list = get_wifi_list()
                # wifi network is still connecting:
                command = 'nmcli -f GENERAL.CONNECTION dev show wlan0'
                try:
                    wifi_connected = os.popen(command).read().split(
                        'GENERAL.CONNECTION: ')[1].strip()
                    known_wifi_list = know_wifi_list()
                    try:
                        connected_to_ip = get_ip_from_wifi_connected()
                    except:
                        connected_to_ip = ''
                    return render_template('./wifi/wifi.html', wifi_list=wifi_list, signal_list=signal_list, security_list=security_list, wifi_connected=wifi_connected, known_wifi_list=known_wifi_list, connected_to_ip=connected_to_ip)
                except Exception as err:
                    # print(err)
                    error = "Thiết bị này không hỗ trợ mạng WIFI"
                    return render_template('./index.html', error=error)
            else:
                return render_template('./index.html')
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/access_wifi', methods=['GET', 'POST'])
def access_wifi():
    is_connect_with_old_wifi()
    # get list wifi that've used
    wifi = request.args.get('wifi').replace(' ', '\ ')
    list_wifi = name_know_wifi_list(wifi)
    if wifi in list_wifi:
        # connect wifi which have used
        return_code = connect_old_wifi(wifi)
        ip = get_ip_from_wifi_connected()
        if return_code.split(" ")[0] == "Error":
            return jsonify(result="Failed")
        else:
            return jsonify(result="Successed", ip=ip)
    else:
        # connect wifi new
        wifi = request.args.get('wifi').replace(' ', '\ ')
        pwd = request.args.get('pwd')
        return_code = connect_new_wifi(wifi, pwd)

        if ('failed' in return_code):
            wifi = request.args.get('wifi').replace(' ', '\ ')
            return_code = delete_wifi(wifi)
            return jsonify(result='Failed')
        ip = get_ip_from_wifi_connected()
        if return_code.split(" ")[0] == "Error":
            return jsonify(result="Failed")
        else:
            return jsonify(result="Successed", ip=ip)


@mod.route('/disconnect_wifi', methods=['GET', 'POST'])
def disconnect_wifi():
    wifi = request.args.get('wifi')
    return_code = disconnect(wifi)
    return jsonify()


@mod.route('/check_wifi_exist', methods=['GET', 'POST'])
def check_wifi_exist():
    wifi = request.args.get('wifi').replace(' ', '\ ')
    list_wifi = check_exist_wifi()
    if wifi in list_wifi:
        return jsonify(result="Exist")
    else:
        return jsonify(result="OK")


@mod.route('/manage_known_networks', methods=['GET', 'POST'])
def manage_known_networks():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                # wifi networks available to connect:
                wifi_list, signal_list, security_list = get_wifi_list()
                # wifi network is still connecting:
                wifi_list = know_wifi_list()
                return render_template('./wifi/wifi_list.html', wifi_list=wifi_list)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@mod.route('/delete_wifi', methods=['GET', 'POST'])
def delete():
    wifi = request.args.get('wifi').replace(' ', '\ ')
    return_code = delete_wifi(wifi)
    return jsonify(result=return_code)
