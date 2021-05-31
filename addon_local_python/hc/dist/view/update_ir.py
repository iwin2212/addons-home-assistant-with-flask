from flask import render_template, session, Blueprint
import logging
mod = Blueprint('update_ir', __name__)


@mod.route('/update_ir')
def update_ir():
    if 'logged_in' in session:
        if session['logged_in']:
            # try:
                return render_template('./update_ir/update_ir.html')
            # except Exception as error:
            #     logging.warning("Error: {}".format(error))
            #     return render_template('./index.html', error='Thiết bị đang khởi động. Vui lòng thử lại sau')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')
