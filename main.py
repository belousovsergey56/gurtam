"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""
import os

from flask import Flask, redirect, render_template, url_for

# from flask_bootstrap import Bootstrap

# from flask_login import current_user, login_required, login_user, logout_user

from forms import UploadFile

from gurtam import checking_object_on_vialon, get_ssid, group_update
from gurtam import remove_groups

# from models import User

from read_file import read_json, xls_to_json

# from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# Bootstrap(app)

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))


@app.route('/')
def home() -> str:
    """Render home page.

    Returns:
        str: displays the home page of the application
    """
    return render_template('index.html')


@app.route('/export', methods=['GET', 'POST'])
def export_fms4():
    """_summary_

    Returns:
        _type_: _description_
    """    
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        xls_to_json('upload/{0}'.format(filename))
        a = read_json()
        checking_object_on_vialon(a)
        group_update(a)
        os.remove('upload/{0}'.format(filename))
        os.remove('upload/work_file.json')
        return redirect(url_for('export_fms4'))
    return render_template('export_fms4.html', form=form)


@app.route('/remove_groups', methods=['GET', 'POST'])
def remove_group():
    """_summary_

    Returns:
        _type_: _description_
    """    
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        xls_to_json('upload/{0}'.format(filename))
        a = read_json()
        sid = get_ssid()
        remove_groups(sid, a)
        os.remove('upload/{0}'.format(filename))
        os.remove('upload/work_file.json')
        return redirect(url_for('remove_group'))
    return render_template('remove_groups.html', form=form)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
