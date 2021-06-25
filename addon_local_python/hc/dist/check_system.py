from flask import Flask, jsonify
import requests
import os
import logging
app = Flask(__name__)

local_ip = "127.0.0.1"

@app.route('/check_mxapi', methods=['POST'])
def check_mxapi():
    MXAPI_URL = "http://"+local_ip+":8055/api/info"
    HASS_URL = "http://"+local_ip+":8123/api/states"

    def check():
        res = requests.get(MXAPI_URL)
        if res.status_code != 200:
            logging.warning("Lỗi MXAPI. Đang fix lỗi MXAPI...")
            os.system("service mxapi restart")
            os.system("service avahi-daemon restart")
            logging.warning("Đã fix lỗi MXAPI")
            return jsonify(logging="Đã fix lỗi MXAPI")
        else:
            token = res.json()["token"]
            res = requests.get(HASS_URL, headers={
                "authorization": f"Bearer {token}"})
            if res.status_code == 401:
                logging.warning(
                    "Lỗi token Home Assistant. Vui lòng kiểm tra lại!")
                return jsonify(logging="Lỗi token Home Assistant. Vui lòng kiểm tra lại!")
            elif res.status_code == 200:
                logging.warning("JAVIS HC hoạt động bình thường.")
                return jsonify(logging="JAVIS HC hoạt động bình thường.")
            else:
                logging.warning("Vui lòng đợi Home Assistant khởi động xong!")
                return jsonify(logging="Vui lòng đợi Home Assistant khởi động xong!")
    return check()


@app.route('/check_mxha', methods=['POST'])
def check_mxha():
    try:
        os.system("service mxha restart")
        logging.warning("Đang khởi động lại dịch vụ kết nối đến cloud...")
        return {"logging": "restart mxha"}
    except Exception as error:
        return {"logging": error}


@app.route('/release_log', methods=['POST'])
def release_log():
    try:
        logging.warning("Xoá log và giải phóng dung lượng")
        import subprocess
        cmd = ["truncate", "-s", "0", "/var/lib/docker/containers/*/*-json.log"]
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        return jsonify(logging=output)
    except:
        return jsonify(logging="error")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=123, debug=True)
