from flask import Flask, render_template, request, session, jsonify, send_file, Blueprint
from yaml_util import yaml2dict, dict2yaml, is_nocontent
from utils import *
from no_accent_vietnamese import no_accent_vietnamese
import time
mod = Blueprint('sim', __name__)


@mod.route('/sim')
def sim():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            info = request.args.get('info')
            if info != None:
                info = "Thêm thiết bị thành công."
            sim_file = os.path.join(ROOT_DIR, 'packages/smarthome_sim.yaml')
            check_exist(sim_file)
            list_sim = yaml2dict(sim_file)
            try:
                id_string = list_sim['script']['goiso1']['sequence'][0]['data']['topic'].split(
                    '/')[0]
            except:
                id_string = ''
            # print(id_string)
            return render_template('./sim/sim.html', id_string=id_string, info=info)
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/get_sim_info')
def get_sim_info():
    try:
        ip = request.args.get('ip')
        res = requests.get('http://' + ip + '/api/info')
        return res.text
    except:
        return "Không kết nối được IP"


@mod.route('/add_sim')
def add_sim():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            return render_template('./sim/add_sim.html', err='', success='')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')


@mod.route('/delete_sim')
def delete_sim():
    dict_sim = {}
    sim_file = os.path.join(ROOT_DIR, 'packages/smarthome_sim.yaml')
    dict2yaml(dict_sim, sim_file)
    return sim()


@mod.route('/add_sim', methods=['GET', 'POST'])
def add_sim_result():
    if 'logged_in' in session:
        if session['logged_in']:
            if request.method == 'GET':
                return render_template('./packages/smarthome_sim.html', err='', success='')
            else:
                ip = request.form['ip']
                try:
                    response = requests.get(
                        'http://' + ip + '/api/info', timeout=15)
                except:
                    err = 'Không kết nối được với địa chỉ ' + ip + ", xin kiểm tra lại thông tin"
                    return render_template('./switch_mqtt/add_mqtt.html', err=err, success='')

                data = json.loads(str(response.text).replace("\'", "\""))

                id_string = data['netid']
                # print(id_string)
                filename = os.path.join(
                    ROOT_DIR, 'packages/smarthome_sim.yaml')
                data = {'input_text':
                        {
                            'noi_dung_bao_trom': {'name': 'Nhập Tiếng Việt Không Dấu Tin Nhắn Cảnh Báo Đột Nhập.'},
                            'noi_dung_bao_chay': {'name': 'Nhập Tiếng Việt Không Dấu Tin Nhắn Cảnh Báo Rò Rỉ.'},
                            'so_dien_thoai_1': {'name': 'Nhập Số Điện Thoại 1'},
                            'so_dien_thoai_2': {'name': 'Nhập Số Điện Thoại 2'},
                            'so_dien_thoai_3': {'name': 'Nhập Số Điện Thoại 3'}
                        },
                        'script': {
                            'app_goiso1': {'alias': 'Gọi đến SĐT 1', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_1.state}}', 'topic': id_string + '/smart/gms/call'}, 'service': 'mqtt.publish'}]},
                            'app_goiso2': {'alias': 'Gọi đến SĐT 2', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_2.state}}', 'topic': id_string + '/smart/gms/call'}, 'service': 'mqtt.publish'}]},
                            'app_goiso3': {'alias': 'Gọi đến SĐT 3', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_3.state}}', 'topic': id_string + '/smart/gms/call'}, 'service': 'mqtt.publish'}]},
                            'app_goi3so': {'alias': 'Gọi đến cả 3 SĐT', 'sequence': [{'service': 'script.goiso1'}, {'delay': '00:00:21'}, {'service': 'script.goiso2'}, {'delay': '00:00:21'}, {'service': 'script.goiso3'}, {'delay': '00:00:21'}]},
                            'app_smstromso1': {'alias': 'SMS cảnh báo đột nhập đến SĐT 1', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_1.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_trom.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smstromso2': {'alias': 'SMS cảnh báo đột nhập đến SĐT 2', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_2.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_trom.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smstromso3': {'alias': 'SMS cảnh báo đột nhập đến SĐT 3', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_3.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_trom.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smstrom3so': {'alias': 'SMS cảnh báo đột nhập đến cả 3 SĐT', 'sequence': [{'service': 'script.smstromso1'}, {'delay': '00:00:10'}, {'service': 'script.smstromso2'}, {'delay': '00:00:10'}, {'service': 'script.smstromso3'}, {'delay': '00:00:10'}]},
                            'app_smschayso1': {'alias': 'SMS báo cháy đến SĐT 1', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_1.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_chay.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smschayso2': {'alias': 'SMS báo cháy đến SĐT 2', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_2.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_chay.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smschayso3': {'alias': 'SMS báo cháy đến SĐT 3', 'sequence': [{'data': {'payload_template': '{{states.input_text.so_dien_thoai_3.state}}', 'topic': id_string + '/smart/gms/number'}, 'service': 'mqtt.publish'}, {'delay': '00:00:01'}, {'data': {'payload_template': '{{states.input_text.noi_dung_bao_chay.state}}', 'topic': id_string + '/smart/gms/mess'}, 'service': 'mqtt.publish'}]},
                            'app_smschay3so': {'alias': 'SMS báo cháy đến cả 3 SĐT', 'sequence': [{'service': 'script.smschayso1'}, {'delay': '00:00:10'}, {'service': 'script.smschayso2'}, {'delay': '00:00:10'}, {'service': 'script.smschayso3'}, {'delay': '00:00:10'}]}}
                        }
                dict2yaml(data, filename)
                return sim()
        else:
            return render_template('./login.html')
    else:
        return render_template('./login.html')
