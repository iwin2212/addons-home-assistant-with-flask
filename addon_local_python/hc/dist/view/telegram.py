from flask import Blueprint, render_template, session
from flask.globals import request
from flask.json import jsonify
from utils import file_existed
from const import ROOT_DIR
import os
from yaml_util import yaml2dict, dict2yaml
import logging
import yaml
mod = Blueprint('telegram', __name__)


def check_telegram_acc(path=os.path.join(ROOT_DIR, "packages/telegram.yaml")) -> dict:
    if (file_existed(path)):
        data = yaml2dict(path)
        return data
    else:
        from account import telegram_account
        return telegram_account


@mod.route('/telegram')
def telegram():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                telegram_data = check_telegram_acc()
                telegram_data = "".join(str(telegram_data).split("@"))
                telegram_data = yaml.safe_load(telegram_data)
                return render_template('./telegram/telegram.html', telegram_data=telegram_data)
            except Exception as error:
                logging.warning("Error: {}".format(error))
                return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/save_telegram', methods=['POST'])
def save_telegram():
    acc = {'telegram_bot': [{'platform': 'polling', 'api_key': request.args.get('api_key'), 'allowed_chat_ids': [int(request.args.get('chat_id'))]}], 'notify': [{'platform': 'telegram', 'name': 'telegram', 'chat_id': int(request.args.get('chat_id'))}, {
    'name': 'Telegram_Call', 'platform': 'rest', 'resource': 'http://api.callmebot.com/start.php', 'data': {'source': 'HA', 'user': "@" + "".join(str(request.args.get('user')).split("@")), 'lang': 'vi-VN-Wavenet-A', 'rpt': int(request.args.get('rpt'))}}]}
    dict2yaml(acc, os.path.join(ROOT_DIR, "packages/telegram.yaml"))
    return jsonify({"require": "restart"})
