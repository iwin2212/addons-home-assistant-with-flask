from flask import render_template, session, Blueprint, request
from utils import get_info_dev, get_javis_dev, write_javis_dev
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import requests
import json
from const import local_ip
mod = Blueprint('javis_ir', __name__)
cmd = ""

username = 'javis'
password = 'javis2020'
hostname = local_ip

@mod.route('/javis_ir')
def javis_ir():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            device = get_javis_dev()
            return render_template('./javis_ir/javis_ir.html', device=device)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/add_javis_ir', methods=['POST'])
def add_javis_ir():
    ip_addr = request.args.get("ip")
    data = get_info_dev(ip_addr)
    if data['model'] == "JSIR01":
        data["ip"] = ip_addr
        javis_dev = get_javis_dev()
        for dev in javis_dev:
            if (dev['netid'] == data["netid"]):
                javis_dev.remove(dev)
        javis_dev.append(data)
        write_javis_dev(javis_dev)
        return {"result": data}
    else:
        data = {"error": "Failed to establish a new connection"}
        return {"result": data}


@mod.route('/delete_javis_ir', methods=['POST'])
def delete_javis_ir():
    try:
        netid = request.args.get("netid")
        javis_dev = get_javis_dev()
        for dev in javis_dev:
            if (dev['netid'] == netid):
                javis_dev.remove(dev)
        write_javis_dev(javis_dev)
        return {"error": False}
    except:
        return {"error": True}


@mod.route('/learning_with_smart_ir', methods=['POST'])
def learning_with_smart_ir():
    username, password, hostname
    netid = request.args.get("entity_id")
    publish_mqtt_to_learn(netid)
    subscribe.callback(on_message_print, topics=[netid+"/remote/learn"], auth={
                       'username': username, 'password': password}, hostname=hostname)
    return {"cmd": cmd}


def publish_mqtt_to_learn(netid):
    username, password, hostname = get_mqtt_info()
    msgs = [{'topic': netid+"/remote/learnset", 'payload': "true"}]
    publish.multiple(msgs, hostname=hostname, auth={
                     'username': username, 'password': password})


def on_message_print(client, userdata, message):
    global cmd
    cmd = message.payload.decode()
    client.disconnect()


def get_mqtt_info():
    global username, password, hostname
    def get_mqtt_entry_id():
        url = "http://127.0.0.1:8123/api/config/config_entries/entry"

        payload = ""
        headers = {
                'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxZGQwYjNlNWE2ZTc0ZTY5YTM5NzdlZDAxMWE2Mjk5OCIsImlhdCI6MTU5NTE4MDYyOCwiZXhwIjoxOTEwNTQwNjI4fQ.9IytiXHV98pS4x5nxhH7z1QAq91ZXzBQaeJsZ8U2ZAQ',
                'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload).json()
        mqtt_entry_id = [i for i in response if (i['domain'] == 'mqtt')]
        if (len(mqtt_entry_id)!=0):
            return (mqtt_entry_id[0]['entry_id'])
        else:
            return ""
    mqtt_entry_id = get_mqtt_entry_id()
    url = "http://127.0.0.1:8123/api/config/config_entries/options/flow"

    payload = json.dumps({"handler":mqtt_entry_id,"show_advanced_options":True})
    headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIxZGQwYjNlNWE2ZTc0ZTY5YTM5NzdlZDAxMWE2Mjk5OCIsImlhdCI6MTU5NTE4MDYyOCwiZXhwIjoxOTEwNTQwNjI4fQ.9IytiXHV98pS4x5nxhH7z1QAq91ZXzBQaeJsZ8U2ZAQ',
            'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()['data_schema']
    for i in response:
        if (i['name'] == 'username'):
            username = i['description']['suggested_value']
        if (i['name'] == 'password'):
            password = i['description']['suggested_value']
        if (i['name'] == 'broker'):
            hostname = i['default']
            if (i['default'] == "localhost"):
                hostname = local_ip
    return username, password, hostname
