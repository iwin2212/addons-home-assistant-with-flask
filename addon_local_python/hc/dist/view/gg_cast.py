from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('gg_cast', __name__)


@mod.route('/gg_cast')
def gg_cast():
    if 'logged_in' in session:
        if session['logged_in']:
            try:
                result = request.args.get('error')
                require_restart = request.args.get('require_restart')
                try:
                    list_gg_cast = get_list_via_integration('cast')
                except Exception as err:
                    return str(err)
                return render_template('./gg_cast/gg_cast.html', list_gg_cast=list_gg_cast, result=result, require_restart=require_restart)
            except:
                return render_template(
                    'index.html', error='Kết nối đến HA bị lỗi. Vui lòng thử lại sau')
    return render_template('./login.html', error='')


@mod.route('/add_gg_cast')
def add_gg_cast():
    if 'logged_in' in session:
        if session['logged_in']:
            return render_template('./gg_cast/add_gg_cast.html')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/config_gg_cast', methods=['GET', 'POST'])
def add_gg_cast_handler():
    result = config_integration_device('cast', '', '', '')
    return jsonify(result)


@mod.route('/delete_gg_cast', methods=['POST'])
def delete_gg_cast():
    entity_id = request.args.get('id')
    result = delete_entity_via_integration('cast', entity_id)
    logging.warning("result -----------------> {0}".format(result))
    try:
        err = result['error']
        require_restart = str(result['require_restart'])
        list_gg_cast = get_list_via_integration('cast')
        return render_template('gg_cast/gg_cast.html', list_gg_cast=list_gg_cast, result=err, require_restart=require_restart)
    except:
        return render_template('index.html', error='Kết nối đến HA bị lỗi. Vui lòng thử lại sau')
