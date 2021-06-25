from const import local_ip, ROOT_DIR
from utils import get_token
import json
from websocket import create_connection
import requests
from flask import render_template, session, Blueprint, jsonify
import logging
import os
mod = Blueprint('update_ir', __name__)


def check_notification_update_smartir():
    ws = create_connection("ws://"+local_ip+":8123/api/websocket")
    result = ws.recv()

    payload = {
        "type": "auth",
        "access_token": get_token()
    }
    ws.send(json.dumps(payload))
    result = ws.recv()

    payload = json.dumps({"type": "persistent_notification/get", "id": 1})
    ws.send(payload)
    result = ws.recv()

    notification = json.loads(result)['result']
    try:
        notif = notification[len(notification)-1]['message']
        return notif
    except:
        return ''


def check_update_smartir():
    url = "http://"+local_ip+":8123/api/services/smartir/check_updates"

    payload = ""
    headers = {
        'Authorization': 'Bearer ' + get_token()
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return check_notification_update_smartir()


def check_manifest_url():
    filedir = os.path.join(
        ROOT_DIR + '/custom_components/smartir/' + "__init__.py")

    f = open(filedir, "r")
    text = f.read()
    f.close()

    if ("smartHomeHub" in text):
        f = open(filedir, "w")
        text = text.replace("smartHomeHub", "dinhchinh82")
        f.write(text)
        f.close()
        return "restart"
    else:
        return "OK"


@mod.route('/check_update_ir')
def check_update_ir():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                return render_template('./update_ir/update_ir.html', update=check_update_smartir(), restart=check_manifest_url())
            except Exception as error:
                logging.warning("Error: {}".format(error))
                return render_template('./index.html', error='Dịch vụ Home Assistant chưa sẵn sàng. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/get_update_ir', methods=["POST"])
def get_update_ir():
    try:
        url = "http://"+local_ip+":8123/api/services/smartir/update_component"

        payload = ""
        headers = {
            'Authorization': 'Bearer ' + get_token()
        }

        response = requests.request("POST", url, headers=headers, data=payload)
    except Exception as error:
        return render_template('./index.html', error='Dịch vụ Home Assistant chưa sẵn sàng. Vui lòng thử lại sau. Error: {}'.format(error))
    return jsonify(response=check_notification_update_smartir())
