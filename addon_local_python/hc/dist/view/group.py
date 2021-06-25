from flask import render_template, session, Blueprint
mod = Blueprint('group', __name__)


@mod.route('/govern_group')
def govern_group():
    if 'logged_in' in session:
        if session['logged_in'] == True:
            
            return render_template('./group/group.html')
        return render_template('./login.html', error='')
    return render_template('./login.html', error='')
