from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
from const import *
mod = Blueprint('camera', __name__)


@mod.route('/camera')
def camera():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            list_camera = []
            camera = {}
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            filename = os.path.join(ROOT_DIR, 'camera.yaml')
            check_exist(filename)
            data = yaml2dict(filename)
            for item in data:
                try:
                    camera['name'] = item['name']
                    camera['platform'] = item['platform']
                    camera['input'] = item['input']
                    list_camera.append(camera)
                    camera = {}
                except Exception as error:
                    logging.warning("Error: {}".format(error))
                    continue
            return render_template('./camera/camera.html', list_camera=list_camera, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_camera', methods=['GET', 'POST'])
def add_camera():
    if request.method == 'POST':
        data = []
        # get 'name', 'username', 'password', 'ip' from request & generate 'still_image_url', 'stream_source'
        name = replace_space(request.form['name'])
        username = replace_space(request.form['username'])
        password = request.form['password']
        ip = request.form['ipaddr']
        port = request.form['port']
        params = request.form['params']
        stream_source = 'rtsp://' + username + ':' + password + '@' + ip + ':' + port + params
        # save file to camera.yaml
        dict_camera = {}
        data = yaml2dict(os.path.join(ROOT_DIR, 'camera.yaml'))

        dict_camera['platform'] = 'ffmpeg'
        dict_camera['name'] = name
        dict_camera['input'] = stream_source

        data.append(dict_camera)
        dict2yaml(data, os.path.join(ROOT_DIR, 'camera.yaml'))
        return camera()
    return render_template("camera/add_camera.html")


@mod.route('/show_video')
def show_video():
    allow_list = ['mp4', 'jpg']
    dir_ = os.path.join(ROOT_DIR, "tmp/camera")
    if os.path.isdir(dir_) == False:
        os.mkdir(dir_)
    onlyfiles = [f for f in os.listdir(dir_) if os.path.isfile(
        os.path.join(dir_, f)) and (os.path.basename(f).split('.')[1] in allow_list)]
    # print(onlyfiles)
    return render_template("camera/show_video.html", namefiles=onlyfiles)


@mod.route('/del_file', methods=['POST'])
def del_file():
    name = request.args.get('name')
    file_dir = os.path.join(ROOT_DIR, "tmp/camera", name)
    try:
        # print(file_dir)
        os.remove(file_dir)
        # print("File Removed!")
    except:
        # print("File Not Removed!")
        pass
    return show_video()


@mod.route('/delete_camera', methods=['POST'])
def delete_camera():
    if request.method == 'POST':
        name = request.args.get('name')
        _dir = os.path.join(ROOT_DIR, 'camera.yaml')
        list_device = yaml2dict(_dir)
        devices = []
        for i in list_device:
            if 'name' in i.keys():
                if i['name'] != name:
                    devices.append(i)
            else:
                devices.append(i)
        list_device = devices
        dict2yaml(list_device, _dir)
        return camera()
