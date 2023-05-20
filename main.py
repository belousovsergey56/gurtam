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

from gurtam import create_object, get_ssid, group_update
from gurtam import remove_groups, get_object_id
from gurtam import fill_info5, check_create_info5, check_info
from gurtam import update_param
from gurtam import fill_info

from models import User

from tools import read_json, xls_to_json, send_mail

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime
from time import strftime, gmtime


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
            with open('logging/log_report.txt', 'a') as report:
                text = f'{datetime.now().ctime()} - {user.login} - sign in\n'
                report.write(text)
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
    with open('logging/log_report.txt', 'a') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            text = f'{datetime.now().ctime()} - {user.login} - open home page\n'
            report.write(text)
    return render_template('index.html')


@app.route('/export', methods=['GET', 'POST'])
@login_required
def export_fms4():
    """Import object data to Wialon.

    Returns:
        Html template export_fms4.html
    """
    with open('logging/log_report.txt', 'a') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            text = f'{datetime.now().ctime()} - {user.login} - open page import on fms4\n'
            report.write(text)
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        import_list = read_json(file_path)
        sid = get_ssid()
        start = datetime.now()
        counter = 0
        with open('logging/import_report.txt', 'w') as log:
            log.write(f'Время начала: {start.ctime()}\n')
            log.write(f'{import_list[0].get("ЛИЗИНГ")}\n')
        for unit in import_list:
            unit_id = get_object_id(sid, unit.get('ИМЕЙ'))
            unit.update({'uid': unit_id})
            if unit_id == -1:
                new_id = create_object(sid, unit_id, unit)
                unit.update({'uid': new_id})
                id_info4 = check_info(sid, new_id, 'Инфо4')
                update_param(sid, new_id, unit, id_info4[0])
                counter += 1
            else:
                id_info4 = check_info(sid, unit_id, 'Инфо4')
                update_param(sid, unit_id, unit, id_info4[0])
                counter += 1
        group_update(import_list)
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:S", gmtime(delta_time.total_seconds()))
        with open('logging/import_report.txt', 'a') as log:
            log.write(
                f'''Время окончания: {endtime.ctime()}
Ушло времени на залив данных: {delta_time}
Обработано строк: {counter}'''
                )
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        with open('logging/import_report.txt', 'r') as report:
            id_ = current_user.get_id()
            email = User.query.filter_by(id=id_).first()
            send_mail(email, 'Импорт на виалон', report.read())
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
        file_path = xls_to_json('upload/{0}'.format(filename))
        imei_list = read_json(file_path)
        sid = get_ssid()
        remove_groups(sid, imei_list)
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        return redirect(url_for('remove_group'))
    return render_template('remove_groups.html', form=form)


@app.route('/update_info5', methods=['GET', 'POST'])
def update_info5():
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        file_with_data = read_json(file_path)
        sid = get_ssid()
        counter = 1
        length = len(file_with_data)
        for unit in file_with_data:
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
                    fill_info5(sid, unit_id, id_field, unit.get('Специалис'))
                    counter += 1
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        return redirect(url_for('update_info5'))
    return render_template('update_info5.html', form=form)


@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        file_with_data = read_json(file_path)
        sid = get_ssid()
        counter = 0
        length = len(file_with_data)
        start = datetime.now()
        with open('logging/update_info.txt', 'w') as log:
            log.write(f'Начало загрузки: {start.ctime()}\n')
        for unit in file_with_data:
            try:
                unit_id = get_object_id(sid, int(unit.get('IMEI')))
            except TypeError:
                with open('logging/update_info.txt', 'a') as log:
                    log.write(f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open('logging/update_info.txt', 'a') as log:
                    log.write('{0} - не найден\n'.format(unit.get('ИМЕЙ')))
                    counter += 1
            else:
                id_info1 = check_info(sid, unit_id, 'Инфо1')
                id_info5 = check_info(sid, unit_id, 'Инфо5')
                id_info6 = check_info(sid, unit_id, 'Инфо6')
                id_info7 = check_info(sid, unit_id, 'Инфо7')
                id_value_list = [
                    id_info1,
                    id_info5,
                    id_info6,
                    id_info7
                ]
                fill_info(sid, unit_id, id_value_list, unit)
                print(f'Готово {round(counter / length*100, 2)} %')
                counter += 1
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:S", gmtime(delta_time.total_seconds()))
        with open('logging/update_info.txt', 'a') as log:
            log.write(f'Окончание импорта данных: {endtime.ctime()}\n')
            log.write(f'Ушло времени на залив данных: {delta_time}\n')
            log.write(f'Всего строк обработано: {counter} из {length}\n')
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        with open('logging/update_info.txt', 'r') as report:
            id_ = current_user.get_id()
            email = User.query.filter_by(id=id_).first()
            send_mail(email, 'РДДБ обновление полей ИНФО', report.read())
        return redirect(url_for('update_info'))
    return render_template('update_info.html', form=form)


@app.route('/logout')
def logout():
    with open('logging/log_report.txt', 'a') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            text = f'{datetime.now().ctime()} - {user.login} - logout\n'
            report.write(text)
    logout_user()
    return redirect(url_for('sign_in'))


def add_admin():
    password = os.getenv('admin_password')
    admin = User(
        login='admin',
        password=generate_password_hash(password),
        email=os.getenv('admin_email')
        )
    db.session.add(admin)
    db.session.commit()


def add_tech_crew():
    password = os.getenv('crew_password')
    crew = User(
        login='cesar',
        password=generate_password_hash(password),
        email=os.getenv('crew_email')
        )
    db.session.add(crew)
    db.session.commit()


def add_carcade():
    password = os.getenv('carcade_password')
    carcade = User(
        login='carcade',
        password=generate_password_hash(password),
        email=os.getenv('carcade_email')
        )
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
