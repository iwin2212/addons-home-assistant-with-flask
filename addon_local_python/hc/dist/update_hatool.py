from websocket import create_connection
from pathlib import Path
from flask import Flask, render_template, request, session, jsonify, send_file
import io
import json
from const import *
import os
import requests
from utils import *
import time
import subprocess
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'oh_so_secret'


@app.route('/check_update', methods=['GET', 'POST'])
def check_update():
    service = request.args.get('services')
    try:
        res = requests.get(
            f'https://registry.hub.docker.com/v2/repositories/javishome/{service}/tags/latest').json()
        remoteDigest = res["images"][0]["digest"].strip()
        output = subprocess.check_output(
            ['docker', 'inspect', "--format='{{index .RepoDigests 0}}'", f'javishome/{service}'])
        localDigest = output.strip().decode('utf-8')
        return {'error': localDigest.find(remoteDigest) < 0}
    except:
        return {"error": False}


@app.route('/update', methods=['GET', 'POST'])
def update():
    service = request.args.get('services')
    cmd1 = f"docker pull javishome/{service}"
    cmd2 = f"docker stop {service}"
    cmd3 = f"docker rm {service}"
    cmd4 = f"docker run -d --net=host --privileged --restart unless-stopped -v /usr/share/hassio:/usr/share/hassio -v /usr/local/etc/code.txt:/usr/local/etc/code.txt -v /var/run/dbus:/var/run/dbus --name {service} javishome/{service}"
    try:
        subprocess.check_call(cmd1, shell=True)
        subprocess.check_call(cmd2, shell=True)
        subprocess.check_call(cmd3, shell=True)
        subprocess.check_call(cmd4, shell=True)
        return {"error": False}
    except:
        return {"error": True}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1234, debug=False)
