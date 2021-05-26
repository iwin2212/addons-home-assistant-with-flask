from flask import Blueprint, render_template, session
from flask.globals import request
from flask.json import jsonify
from utils import file_existed
from const import ROOT_DIR
from account import telegram_account
import os
from yaml_util import yaml2dict, dict2yaml
import logging
mod = Blueprint('telegram', __name__)


def check_telegram_acc(path=os.path.join(ROOT_DIR, "packages/telegram.yaml"), require='') -> dict:
    if (file_existed(path)):
        data = yaml2dict(path)
        return data, require
    else:
        dict2yaml(telegram_account, path)
        require = "restart"
        return telegram_account, require


@mod.route('/telegram')
def telegram():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                telegram_data, require = check_telegram_acc()
                return render_template('./telegram/telegram.html', telegram_data=telegram_data, require=require)
            except Exception as error:
                logging.warning("Error: {}".format(error))
                return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/save_telegram', methods=['POST'])
def save_telegram():
    acc = {'telegram_bot': [{'platform': 'polling', 'api_key': request.args.get('api_key'), 'allowed_chat_ids': [int(request.args.get('chat_id'))]}], 'notify': [{'platform': 'telegram', 'name': 'telegram', 'chat_id': int(request.args.get('chat_id'))}, {
    'name': 'Telegram_Call', 'platform': 'rest', 'resource': 'http://api.callmebot.com/start.php', 'data': {'source': 'HA', 'user': "@" + request.args.get('user'), 'lang': 'vi-VN-Wavenet-A', 'rpt': int(request.args.get('rpt'))}}]}
    dict2yaml(acc, os.path.join(ROOT_DIR, "packages/telegram.yaml"))
    return jsonify({"require": "restart"})
