"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""


import os
from functools import wraps

from config import app, db, login_manager

from flask import flash, redirect, render_template, url_for

from flask_login import current_user, login_required, login_user, logout_user

from forms import SigninForm, UploadFile

from gurtam import checking_object_on_vialon, get_ssid, group_update
from gurtam import remove_groups, get_object_id, create_custom_fields
from gurtam import fill_info5, check_create_info5

from models import User

from read_file import read_json, xls_to_json

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() != str(1):
            return render_template('403.html')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def sign_in():
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if not user:
            flash(message="Не верный логин,\
                попробуйте снова или обратитесть к своему администратору")
            return render_template('signin.html', form=form)
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash(message="Не верный пароль, попробуйте снова")
            return render_template(
                "signin.html",
                form=form,
                logged_in=current_user.is_authenticated
                )
    return render_template('signin.html', form=form)


@app.route('/home')
@login_required
def home() -> str:
    """Render home page.

    Returns:
        str: displays the home page of the application
    """
    return render_template('index.html')


@app.route('/export', methods=['GET', 'POST'])
@login_required
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
@login_required
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


@app.route('/update_info', methods=['GET', 'POST'])
def update_info5():
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        xls_to_json('upload/{0}'.format(filename))
        file_with_data = read_json()
        sid = get_ssid()
        counter = 1
        length = len(file_with_data)

        for unit in file_with_data:
            # print(f'Готово {round(counter / length*100, 2)} %')
            unit_id = get_object_id(sid, unit.get('Значение'))
            if unit_id == -1:
                with open('logging/unit_not_found.txt', 'a') as log:
                    log.write('{0} - не найден\n'.format(unit.get('ИМЕЙ')))
                    counter += 1
            else:
                if unit.get('Специалист') == 0:
                    print('РДДБ пустой')
                    counter += 1
                else:
                    print('start ' + unit.get('Группировка'))
                    id_field = check_create_info5(sid, unit_id)
                    fill_info5(sid, unit_id, id_field, unit.get('Специалист'))
                    print(f'Готово {round(counter / length*100, 2)} %')
                    counter += 1
        os.remove('upload/{0}'.format(filename))
        os.remove('upload/work_file.json')
        return redirect(url_for('update_info5'))
    return render_template('update_info5.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


def add_admin():
    password = os.getenv('admin_password')
    admin = User(login='admin', password=generate_password_hash(password))
    db.session.add(admin)
    db.session.commit()


def add_tech_crew():
    password = os.getenv('crew_password')
    crew = User(login='cesar', password=generate_password_hash(password))
    db.session.add(crew)
    db.session.commit()


def add_carcade():
    password = os.getenv('carcade_password')
    carcade = User(login='carcade', password=generate_password_hash(password))
    db.session.add(carcade)
    db.session.commit()


with app.app_context():
    if User.query.all():
        None
    else:
        add_admin()
        add_tech_crew()
        add_carcade()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
