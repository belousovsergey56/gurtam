"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""
import os

from config import app, db, login_manager

from flask import Flask, redirect, render_template, url_for

from flask_login import current_user, login_required, login_user, logout_user

from forms import UploadFile

from gurtam import checking_object_on_vialon, get_ssid, group_update
from gurtam import remove_groups

from models import User

from read_file import read_json, xls_to_json

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home() -> str:
    """Render home page.

    Returns:
        str: displays the home page of the application
    """
    return render_template('index.html')


@app.route('/export', methods=['GET', 'POST'])
def export_fms4():
    """Import object data to Wialon.

    Returns:
        Html template export_fms4.html
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
    """Remove object from group.

    Access to the page to remove objects from groups.
    The user uploads an excel file with two columns IMEI and GROUP,
    the function reads it, finds objects by IMEI id and removes these
    objects from groups.

    Returns:
        Html template remove_groups.html
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


def add_admin():
    password = os.getenv('admin_password')
    admin = User(login='admin', password=generate_password_hash(password))
    db.session.add(admin)
    db.session.commit()


def add_tech_crew():
    password = os.getenv('crew_password')
    crew = User(login='okpp', password=generate_password_hash(password))
    db.session.add(crew)
    db.session.commit()


def add_carcade():
    password = os.getenv('carcade_password')
    carcade = User(login='carcade', password=generate_password_hash(password))
    db.session.add(carcade)
    db.session.commit()


add_admin()
add_tech_crew()
add_carcade()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
