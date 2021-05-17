from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
from websocket import create_connection
mod = Blueprint('homekit', __name__)


@mod.route('/homekit')
def qrpage():
    if 'logged_in' in session:
        if session['logged_in'] == False:
            return render_template('./login.html')
        else:
            try:
                string_wed = "ws://"+local_ip+":8123/api/websocket"
                # print(url)
                secret_data = yaml2dict(os.path.join(ROOT_DIR, 'secrets.yaml'))

                ws = create_connection(string_wed)

                result = ws.recv()

                payload = {
                    "type": "auth",
                    "access_token": secret_data['token']
                }
                ws.send(json.dumps(payload))

                result = ws.recv()

                payload = {"type": "persistent_notification/get", "id": "1"}
                ws.send(json.dumps(payload))

                result = ws.recv()
                data = json.loads(result)['result']

                for i in range(len(data)):
                    if (data[i]['message'].find('![image](') != -1):
                        pin_code, qrcode = data[i]['message'].split(
                            '![image](')
                        pin_code = pin_code.split('### ')[1].split('\n')[0]
                        qrcode = qrcode.split(')')[0]
                        # print('-----------')
                        # print(pin_code)
                        # print(qrcode)
                        # print('-----------')

                error = ''
                qrcode = "http://" + url + ":8123" + qrcode
            except Exception:
                qrcode = ""
                pin_code = ""
                error = "Không lấy được mã home kit"
        return render_template('./homekit/homekit.html', data=data, qrcode=qrcode, pin_code=pin_code, error=error, url=url)
    else:
        return render_template('./login.html')
