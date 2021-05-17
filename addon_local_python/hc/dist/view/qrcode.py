from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
import os
from const import *
from yaml_util import yaml2dict, dict2yaml, is_nocontent
import requests
import re
import time
from utils import *
mod = Blueprint('qrcode', __name__)


@mod.route('/qr')
def qrpage():
    if 'logged_in' in session:
        if session['logged_in'] == False:
            return render_template('./login.html')
        else:
            while True:
                device = get_devices()
                if device == None:
                    return "<h2>Chưa load xong HA, vui lòng đợi 1 lát rồi load lại</h2>"
                else:
                    break
            return render_template('./qrcode/qrcode.html', data=create_qr_data(CODE_FILE))
    else:
        return render_template('./login.html')
