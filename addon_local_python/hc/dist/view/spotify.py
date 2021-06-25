from flask import Blueprint, render_template, session
from flask.globals import request
from flask.json import jsonify
from utils import file_existed
from const import ROOT_DIR, local_ip
import os
from yaml_util import yaml2dict, dict2yaml
import shutil
import logging
import requests
mod = Blueprint('spotify', __name__)


# def check_spotify_account(path=os.path.join(ROOT_DIR, "packages/spotify.yaml"), require='') -> dict:
#     if ((file_existed(path)) and file_existed(os.path.join(ROOT_DIR, "custom_components/spotcast"))):
#         data = yaml2dict(path)
#         return data, require
#     else:
#         # clone_custom_components()
#         # dict2yaml(spotify_account, path)
#         require = "error"
#         return spotify_account, require
def check_spotify_account(require='') -> dict:
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
    
    if ((data['result'] ==  'invalid' and 'spotcast' in data['errors']) or os.path.isdir(os.path.join(ROOT_DIR, "custom_components/spotcast")) == False):
        require = 'error'
        spotify_yaml = os.path.join(ROOT_DIR, "packages/spotify.yaml")
        if (file_existed(spotify_yaml)):
            os.remove(spotify_yaml)
    return require


def clone_custom_components(temp_path=ROOT_DIR, dst=os.path.join(ROOT_DIR, "custom_components"), clone="git clone https://github.com/fondberg/spotcast.git") -> str:
    # os.system("sshpass -p your_password ssh user_name@your_localhost")
    # Specifying the path where the cloned project needs to be copied
    os.chdir(temp_path)
    try:
        logging.warning("Clone Spotcast from Github")
        if (os.system(clone) == 0):  # Cloning
            src = os.path.join(temp_path, "spotcast/custom_components")
            logging.warning("Copy Spotcast into custom_components")
            shutil.copytree(os.path.join(src, 'spotcast'),
                            os.path.join(dst, 'spotcast'))
            shutil.rmtree(os.path.join(temp_path, "spotcast"))
            logging.warning("Done.")
            return "done"
    except Exception as error:
        logging.warning("Spotcast exists")
        if ('File exists' in str(error)):
            shutil.rmtree(os.path.join(temp_path, "spotcast"))
            return 'done'


@mod.route('/spotify')
def spotify():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                require = check_spotify_account()
                spotify_yaml_path = os.path.join(ROOT_DIR, "packages/spotify.yaml")
                if (file_existed(spotify_yaml_path)):
                    spotify_account = yaml2dict(spotify_yaml_path)
                else:
                    from account import spotify_account
                return render_template('./spotify/spotify.html', spotify_data=spotify_account, require=require)
            except Exception as error:
                logging.warning("Error: {}".format(error))
                return render_template('./index.html', error='Home Assistant chưa sắn sàng. Vui lòng kiểm tra và thử lại')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/save_spotify_acc', methods=['POST'])
def save_spotify_acc():
    acc = {'spotify': {'client_id': request.args.get('client_id'), 'client_secret': request.args.get('client_secret')}, 'spotcast': {
        'sp_dc': request.args.get('sp_dc'), 'sp_key': request.args.get('sp_key')}}
    dict2yaml(acc, os.path.join(ROOT_DIR, "packages/spotify.yaml"))
    return jsonify({"require":"restart"})
