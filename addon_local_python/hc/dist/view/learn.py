from flask import render_template, request, session, jsonify, Blueprint
from yaml_util import yaml2dict
from utils import *
import time
from view.media import list_TV
from view.climate import climate_rm
from learn_command import learning_command_with_ir, learning_command_rf
mod = Blueprint('learn', __name__)


@mod.route('/learn_command', methods=['POST'])
def command_handle():
    entity_id = request.args.get('entity_id')
    p = learning_command_with_ir(entity_id)
    return jsonify(result=p)


@mod.route('/learn_command_rf', methods=['POST'])
def command_handling():
    entity_id = request.args.get('entity_id')
    name = entity_id.split('.')[1].split('_remote')[0]
    remote_data = get_info_broadlink(name)
    host = remote_data[0]['data']['host']
    mac = remote_data[0]['data']['mac']
    model = get_model_broadlink(name)
    p = learning_command_rf(mac, host, model)
    return jsonify(result=p)
