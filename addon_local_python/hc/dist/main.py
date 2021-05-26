from view import air_condition, scripts_manager, newspaper, qrcode, media, gateway_xiaomi, sensor, wifi, homekit, alarm, automation, camera, sim, switch, climate, fan, light, xiaomi, learn, e_measure, gg_cast, switchbot, count_down, spotify,telegram
from flask import Flask, render_template, request, session, send_file
from yaml_util import yaml2dict, dict2yaml
from const import *
import os
import requests
from utils import *
import subprocess
##Addons
app = Flask(__name__, static_folder='/static', template_folder='/templates')
##Chạy trực tiếp 5005
# app = Flask(__name__)
app.config['SECRET_KEY'] = 'oh_so_secret'

app.register_blueprint(air_condition.mod)
app.register_blueprint(scripts_manager.mod)
app.register_blueprint(newspaper.mod)
app.register_blueprint(qrcode.mod)
app.register_blueprint(media.mod)
app.register_blueprint(gateway_xiaomi.mod)
app.register_blueprint(sensor.mod)
app.register_blueprint(homekit.mod)
app.register_blueprint(alarm.mod)
app.register_blueprint(automation.mod)
app.register_blueprint(camera.mod)
app.register_blueprint(sim.mod)
app.register_blueprint(switch.mod)
app.register_blueprint(climate.mod)
app.register_blueprint(fan.mod)
app.register_blueprint(light.mod)
app.register_blueprint(xiaomi.mod)
app.register_blueprint(learn.mod)
app.register_blueprint(wifi.mod)
app.register_blueprint(e_measure.mod)
app.register_blueprint(gg_cast.mod)
app.register_blueprint(switchbot.mod)
app.register_blueprint(count_down.mod)
app.register_blueprint(spotify.mod)
app.register_blueprint(telegram.mod)


@app.route('/login')
def login():
    return render_template('./login.html', error='')


@app.route('/login', methods=['POST'])
def login_handle():
    secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))
    session['logged_in'] = False
    user_password = request.form['password']
    if user_password == secret_data['http_password']:
        session['logged_in'] = True
        return render_template('./index.html')
    else:
        return render_template("./login.html", error='Đăng nhập không thành công, hãy thử lại')


@app.route('/change_password')
def change_password():
    if 'logged_in' in session:
        if session['logged_in']:
            error = ''
            return render_template('./change_password.html', error=error)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@app.route('/change_password', methods=['POST'])
def change_password_handle():
    filename = os.path.join(ROOT_DIR, 'secrets.yaml')
    secret_data = yaml2dict(filename)
    old_password = request.form['old_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    if old_password != secret_data['http_password']:
        error = 'Mật khẩu sai'
        return render_template('./change_password.html', error=error)
    if new_password != confirm_password:
        error = 'Mật khẩu xác nhận không khớp'
        return render_template('./change_password.html', error=error)
    if new_password == old_password:
        error = 'Mật khẩu mới giống mật khẩu cũ'
        return render_template('./change_password.html', error=error)
    secret_data['http_password'] = new_password
    fi = open(CODE_FILE, 'r').readlines()
    # print(fi)
    fi[1] = new_password + "\n"
    f = open(CODE_FILE, 'w')
    for i in fi:
        f.write(i)
    f.close()

    dict2yaml(secret_data, filename)
    return login()


@app.route('/')
def index():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            return render_template('./index.html')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@app.route('/add_input_boolean', methods=['GET', 'POST'])
def add_input_boolean():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == "GET":
                return render_template('./toilet/add_input_boolean.html')
            else:
                check_exist(os.path.join(ROOT_DIR, 'input_boolean.yaml'))
                list_input_boolean = yaml2dict(
                    os.path.join(ROOT_DIR, 'input_boolean.yaml'))
                list_input_boolean[request.form['id']] = {
                    "name": request.form['name'],
                    "initial": False
                }
                dict2yaml(list_input_boolean, os.path.join(
                    ROOT_DIR, 'input_boolean.yaml'))
                return render_template('./toilet/input_boolean.html', list_input_boolean=list_input_boolean)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@app.route('/input_boolean')
def input_boolean():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            check_exist(os.path.join(ROOT_DIR, 'input_boolean.yaml'))
            list_input_boolean = yaml2dict(
                os.path.join(ROOT_DIR, 'input_boolean.yaml'))
            return render_template('./toilet/input_boolean.html', list_input_boolean=list_input_boolean)
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@app.route('/delete_input_boolean', methods=['POST'])
def delete_input_boolean():
    iden = request.args.get('iden')
    list_input_boolean = yaml2dict(
        os.path.join(ROOT_DIR, 'input_boolean.yaml'))
    del list_input_boolean[iden]
    dict2yaml(list_input_boolean, os.path.join(ROOT_DIR, 'input_boolean.yaml'))
    check_exist(os.path.join(ROOT_DIR, 'input_boolean.yaml'))
    list_input_boolean = yaml2dict(
        os.path.join(ROOT_DIR, 'input_boolean.yaml'))
    return render_template('./toilet/input_boolean.html', list_input_boolean=list_input_boolean)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return render_template('./login.html', error='')


@app.route('/homeassistant')
def home_assistant():
    info = ''
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/check_config', methods=['POST'])
def check_config():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip+':8123/api/config/core/check_config'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    data = res.json()
    # print(data)
    return render_template('./homeassistant.html', info='', config_result=data['result'], config_err=data['errors'])


@app.route('/reload_core', methods=['POST'])
def reload_core():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip + \
        ':8123/api/services/homeassistant/reload_core_config'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    info = ''
    if res.status_code == 200:
        info = "Đã gọi service reload core"
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/reload_groups', methods=['POST'])
def reload_groups():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip+':8123/api/services/group/reload'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    info = ''
    if res.status_code == 200:
        info = "Đã gọi service reload group"
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/reload_automations', methods=['POST'])
def reload_automations():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip+':8123/api/services/automation/reload'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    info = ''
    if res.status_code == 200:
        info = "Đã gọi service reload automation"
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/reload_scripts', methods=['POST'])
def reload_scripts():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip+':8123/api/services/script/reload'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    info = ''
    if res.status_code == 200:
        info = "Đã gọi service reload script"
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/restart_server', methods=['POST'])
def restart_server():
    try:
        subprocess.call(['sv', 'down', 'hass'])
        subprocess.call(['pkill', 'hass'])
        subprocess.call(['sv', 'up', 'hass'])
        info = "Đã restart server"
    except:
        secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
        url_service = 'http://'+local_ip+':8123/api/services/homeassistant/restart'
        data = yaml2dict(secret_file)
        authen_code = data['token']
        headers = {
            "Authorization": "Bearer " + authen_code,
            "content-type": "application/json"
        }
        res = requests.post(url_service, headers=headers)
        info = ''
        if res.status_code == 200:
            info = "Đang khởi động lại dịch vụ Javis HC. Xin vui lòng chờ trong giây lát."

    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/stop_server', methods=['POST'])
def stop_server():
    secret_file = os.path.join(ROOT_DIR, 'secrets.yaml')
    url_service = 'http://'+local_ip+':8123/api/services/homeassistant/stop'
    data = yaml2dict(secret_file)
    authen_code = data['token']
    headers = {
        "Authorization": "Bearer " + authen_code,
        "content-type": "application/json"
    }
    res = requests.post(url_service, headers=headers)
    info = ''
    if res.status_code == 200:
        info = "Đã gọi service stop server"
    return render_template('./homeassistant.html', info=info, config_result='')


@app.route('/javis-backup', methods=['POST'])
def backup_data():
    compress_data(os.path.join(data_file, 'javis-backup.zip.bin'), ROOT_DIR)
    try:
        return send_file(os.path.join(data_file, 'javis-backup.zip.bin'), attachment_filename='javis-backup.zip.bin')
    except Exception as e:
        return str(e)


@app.route('/restore', methods=['GET', 'POST'])
def restore():
    if request.method == 'GET':
        err = ''
        return render_template('./restore.html', err=err)
    elif request.method == 'POST':
        file_ = request.files['file']
        file_.save(os.path.join(data_file, file_.filename))
        # print(os.path.join(data_file, file_.filename))
        unzip_file(os.path.join(data_file, file_.filename),
                   os.path.join(data_file, "a"), ROOT_DIR)

        return index()


@app.route('/add_configurator', methods=['GET', 'POST'])
def add_configurator():
    if 'logged_in' in session:
        if session['logged_in'] == False:
            return login()

        if request.method == 'GET':
            try:
                info = request.headers['Referer'].split(":5005")[0]
                url = yaml2dict(os.path.join(ROOT_DIR, 'configurator.yaml'))[
                    'configurator']['url'].split(":3218")[0]
            except Exception:
                url = ""
            return render_template('./config/add_configurator.html', url=url, info=info)
        else:
            data = yaml2dict(os.path.join(ROOT_DIR, 'configurator.yaml'))
            ip = request.form['ip']
            if ip == '':
                ip = None
            else:
                ip += ":3218"
            data["configurator"] = {
                "title": "Configrator",
                "icon": "mdi:wrench",
                "url": ip
            }
            info = "Đã lưu"
            dict2yaml(data, os.path.join(ROOT_DIR, 'configurator.yaml'))
            return index()
    else:
        return login()


@app.route('/add_device_tracker', methods=['GET', 'POST'])
def add_device_tracker():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                return render_template('./add_device_tracker.html')
            else:
                filename = os.path.join(ROOT_DIR, 'device_tracker.yaml')
                check_exist(filename)
                list_device_tracker = yaml2dict(filename)
                ip = request.form['ip']
                if ip not in list_device_tracker[0]['hosts']:
                    list_device_tracker[0]['hosts'].append(ip)
                splited_ip = ip.split(".")
                tail = splited_ip[-1]
                below = ".".join(splited_ip[:-1]) + ".0-" + str(int(tail) - 1)
                above = ".".join(splited_ip[:-1]) + \
                    "." + str(int(tail) + 1) + "-255"
                list_device_tracker[0]['exclude'].append(below)
                list_device_tracker[0]['exclude'].append(above)
                dict2yaml(list_device_tracker, os.path.join(filename))
                return render_template('./index.html')
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@app.route('/add_notify_service', methods=['GET', 'POST'])
def add_notify_service():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            if request.method == 'GET':
                return render_template('./add_notify_service.html')
            else:
                filename = os.path.join(ROOT_DIR, 'notify.yaml')
                data = {
                    "platform": "pushbullet",
                    "name": request.form['name'],
                    "api_key": request.form['key']
                }
                dict2yaml(data, filename)
                return render_template('./index.html')
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')


@app.route('/not_found', methods=['GET', 'POST'])
def not_found():
    return render_template('./error/not_found.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2021, debug=False)
