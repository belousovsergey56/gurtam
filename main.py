"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""
import os
from functools import wraps

from config import app, db, login_manager

from flask import flash, redirect, render_template, url_for
from flask import jsonify

from flask_login import current_user, login_required, login_user, logout_user

from forms import SigninForm, UploadFile, UserForm

from gurtam import create_object, get_ssid, group_update
from gurtam import remove_groups, get_object_id
from gurtam import fill_info5, check_create_info5, check_admin_fields
from gurtam import update_param
from gurtam import fill_info, upd_inn_field, check_custom_fields

from models import User

from tools import read_json, xls_to_json, send_mail, update_bd
from tools import get_diff_in_upload_file

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime
from time import strftime, gmtime

lgroup = {
    'admin': ['gpbal', 'carcade', 'evolution', 'admin', 'cesar'],
    'cesar': ['cesar'],
    'gpbal': ['gpbal'],
    'carcade': ['carcade'],
    'evolution': ['evolution']}


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
    year = datetime.now().year
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if not user:
            flash(message="Не верный логин,\
                попробуйте снова или обратитесть к своему администратору")
            return render_template('signin.html', form=form, year=year)
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            with open('logging/log_report.log', 'a') as report:
                text = f'{datetime.now().ctime()} - {user.login} - sign in\n'
                report.write(text)
            return redirect(url_for('home'))
        else:
            flash(message="Не верный пароль, попробуйте снова")
            return render_template(
                "signin.html",
                form=form,
                year=year
            )
    return render_template('signin.html', form=form, year=year)


@app.route('/home')
@login_required
def home() -> str:
    """Render home page.

    Returns:
        str: displays the home page of the application
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    with open('logging/log_report.log', 'a') as report:
        user = User.query.filter_by(id=current_user.get_id()).first()
        text = f'{datetime.now().ctime()} - {user.login} - open home page\n'
        report.write(text)
    return render_template('index.html', user=user)


@app.route('/owners', methods=['GET', 'POST'])
@login_required
def admin():
    user = User.query.filter_by(id=current_user.get_id()).first()
    database = User.query.all()
    form = UserForm()
    return render_template('admin.html', form=form, user=user, db=database)


@app.route('/create_user', methods=['POST', 'GET'])
@login_required
def create_user():
    form = UserForm()
    leasing = User.query.filter_by(id=current_user.get_id()).first()

    form.group.choices = lgroup.get(leasing.group)
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(
                message='Пользователь с такой почтой уже существует, попробуйте ввести новую почту')
            return redirect(url_for('create_user'))
        new_user = User(
            login=form.login.data,
            email=form.email.data,
            password=generate_password_hash(
                form.password.data, salt_length=13),
            group=form.group.data,
            access_create=form.access_create.data,
            access_remove=form.access_remove.data,
            access_edit=form.access_edit.data
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('create_user.html', form=form, user=leasing)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id: int):
    user = User.query.filter_by(id=current_user.get_id()).first()
    edit_user = User.query.filter_by(id=user_id).first()
    form = UserForm(
        login=edit_user.login,
        email=edit_user.email,
        group=edit_user.group,
        password=edit_user.password,
        access_create=edit_user.access_create,
        access_remove=edit_user.access_remove,
        access_edit=edit_user.access_edit
    )
    form.group.choices = lgroup.get(user.group)
    if form.validate_on_submit():
        edit_user.login = form.login.data
        edit_user.email = form.email.data
        edit_user.group = form.group.data
        edit_user.access_create = edit_user.access_create if user_id == user.id else form.access_create.data
        edit_user.access_remove = edit_user.access_remove if user_id == user.id else form.access_remove.data
        edit_user.access_edit = edit_user.access_edit if user_id == user.id else form.access_edit.data
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template(
        'edit_user.html',
        form=form,
        user_id=edit_user.id,
        user=user
    )


@app.route('/edit_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_password(user_id: int):
    user = User.query.filter_by(id=current_user.get_id()).first()
    edit_password = User.query.filter_by(id=user_id).first()
    form = UserForm(
        login=edit_password.login,
        email=edit_password.email,
        group=edit_password.group,
        password=edit_password.password,
        access_create=edit_password.access_create,
        access_remove=edit_password.access_remove,
        access_edit=edit_password.access_edit
    )
    form.group.choices = lgroup.get(user.group)
    if form.validate_on_submit():
        edit_password.password = generate_password_hash(
            form.password.data, salt_length=13)
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template(
        'edit_password.html',
        form=form,
        user_id=edit_password.id,
        user=user
    )


@app.route('/remove_user/<int:user_id>')
@login_required
def remove_user(user_id: int):
    teacher_to_delete = User.query.get(user_id)
    db.session.delete(teacher_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


def id_fields(sid, new_id) -> dict:
    """
        geozone_sim,
        geozone_imei,
        Vin,
        Марка,
        Модель,
        Пин,
        Инфо4

    """
    map_id = {
        'geozone_imei': check_admin_fields(sid, new_id, 'geozone_imei')[0],
        'geozone_sim': check_admin_fields(sid, new_id, 'geozone_sim')[0],
        'Vin': check_custom_fields(sid, new_id, 'Vin')[0],
        'Марка': check_custom_fields(sid, new_id, 'Марка')[0],
        'Модель': check_custom_fields(sid, new_id, 'Модель')[0],
        'Пин': check_admin_fields(sid, new_id, 'Пин')[0],
        'Инфо4': check_admin_fields(sid, new_id, 'Инфо4')[0]
    }
    return map_id


@app.route('/export', methods=['GET', 'POST'])
@login_required
def export_fms4():
    """Import object data to Wialon.

    Returns:
        Html template export_fms4.html
    """
    with open('logging/log_report.log', 'a') as report:
        user = User.query.filter_by(id=current_user.get_id()).first()
        text = f'{datetime.now().ctime()} - {user.login} - open page import on fms4\n'
        report.write(text)
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        import_list = read_json(file_path)
        if 'Инфо4' not in import_list[0] and 'ДЛ' not in import_list[0] and 'Пин' not in import_list[0]:
            flash(message="Ошибка иморта. Необходимые данные не находятся на первом листе, не соответвуют шаблону или не в формате .XLSX")
            os.remove(f'upload/{filename}')
            os.remove(f'{file_path}.json')
            return render_template(
                "export_fms4.html",
                form=form,
                logged_in=current_user.is_authenticated
            )
        sid = get_ssid()
        start = datetime.now()
        counter = 0
        with open('logging/import_report.log', 'w') as log:
            log.write(f'Время начала: {start.ctime()}\n')
            log.write(f'{import_list[0].get("ЛИЗИНГ")}\n')
        for unit in import_list:
            unit_id = get_object_id(sid, unit.get('geozone_imei'))
            unit.update({'uid': unit_id})
            if unit_id == -1:
                try:
                    new_id = create_object(sid, unit_id, unit)
                    unit.update({'uid': new_id})
                    update_param(sid, new_id, unit, id_fields(sid, new_id))
                    counter += 1
                except AttributeError:
                    counter += 1
            else:
                update_param(sid, unit_id, unit, id_fields(sid, unit_id))
                counter += 1
        group_update(import_list)
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open('logging/import_report.log', 'a') as log:
            log.write(f'Время окончания: {endtime.ctime()}\n')
            log.write(f'Ушло времени на залив данных: {delta_time}\n')
            log.write(f'Обработано строк: {counter}\n')
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        with open('logging/import_report.log', 'r') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'Импорт на виалон', report.read())
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

        if 'ГРУППА' not in imei_list[0] and 'ИМЕЙ' not in imei_list[0]:
            flash(message="Ошибка иморта. Необходимые данные не находятся на первом листе, не соответвуют шаблону или не в формате .XLSX")
            os.remove(f'upload/{filename}')
            os.remove(f'{file_path}.json')
            return render_template(
                "remove_groups.html",
                form=form,
                logged_in=current_user.is_authenticated
            )

        sid = get_ssid()
        start = datetime.now()
        count_lines = len(imei_list)
        with open('logging/remove_group_report.log', 'w') as log:
            log.write(f'Время начала: {start.ctime()}\n')
            log.write(
                f'\nУдаление объектов из группы по маске - {imei_list[0].get("ГРУППА")}\n')
        remove_groups(sid, imei_list)

        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))

        with open('logging/remove_group_report.log', 'a') as log:
            log.write(f'\nВремя окончания: {endtime.ctime()}\n')
            log.write(
                f'Ушло времени на удаление объектов из групп: {delta_time}\n')
            log.write(f'Колличество загруженных строк : {count_lines}\n')
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')

        with open('logging/remove_group_report.log', 'r') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'Удаление объектов из групп', report.read())
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
                    fill_info5(sid, unit_id, id_field, unit.get('Специалист'))
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
        new_file = read_json(file_path)
        file_with_data = get_diff_in_upload_file(new_file)
        if 'РДДБ' not in file_with_data[0] and 'ИНН' not in file_with_data[0] and 'Специалист' not in file_with_data[0]:
            flash(message="Ошибка иморта. Необходимые данные не находятся на первом листе, не соответвуют шаблону или не в формате .XLSX")
            os.remove(f'upload/{filename}')
            os.remove(f'{file_path}.json')
            return render_template(
                "update_info.html",
                form=form,
                logged_in=current_user.is_authenticated
            )
        sid = get_ssid()
        counter = 0
        length = len(file_with_data)
        start = datetime.now()
        with open('logging/update_info.log', 'w') as log:
            log.write(f'Начало загрузки: {start.ctime()}\n')
        for unit in file_with_data:
            try:
                unit_id = get_object_id(sid, unit.get('IMEI'))
            except TypeError:
                with open('logging/update_info.log', 'a') as log:
                    log.write(
                        f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open('logging/update_info.log', 'a') as log:
                    log.write('{0} - не найден\n'.format(unit.get('IMEI')))
                    counter += 1
            else:
                id_info1 = check_admin_fields(sid, unit_id, 'Инфо1')
                id_info5 = check_admin_fields(sid, unit_id, 'Инфо5')
                id_info6 = check_admin_fields(sid, unit_id, 'Инфо6')
                id_info7 = check_admin_fields(sid, unit_id, 'Инфо7')
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
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open('logging/update_info.log', 'a') as log:
            log.write(f'Окончание импорта данных: {endtime.ctime()}\n')
            log.write(f'Ушло времени на залив данных: {delta_time}\n')
            log.write(f'Всего строк обработано: {counter} из {length}\n')
        update_bd(new_file)
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        with open('logging/update_info.log', 'r') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'РДДБ обновление полей ИНФО', report.read())
        return redirect(url_for('update_info'))
    return render_template('update_info.html', form=form)


@app.route('/fill_inn', methods=['GET', 'POST'])
def fill_inn():
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        new_file = read_json(file_path)
        if 'ИНН' not in new_file[0] and 'IMEI' not in new_file[0]:
            flash(message="Ошибка иморта. Необходимые данные не находятся на первом листе, не соответвуют шаблону или не в формате .XLSX")
            os.remove(f'upload/{filename}')
            os.remove(f'{file_path}.json')
            return render_template(
                "fill_inn.html",
                form=form,
                logged_in=current_user.is_authenticated
            )
        sid = get_ssid()
        counter = 0
        length = len(new_file)
        start = datetime.now()
        with open('logging/update_inn.log', 'w') as log:
            log.write(f'Начало загрузки: {start.ctime()}\n')
        for unit in new_file:
            print(unit)
            try:
                unit_id = get_object_id(sid, int(unit.get('IMEI')))
            except TypeError:
                with open('logging/update_inn.log', 'a') as log:
                    print('except but have ifelse bloco..')
                    log.write(
                        f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open('logging/update_inn.log', 'a') as log:
                    print('iffff???')
                    log.write('{0} - не найден\n'.format(unit.get('ИМЕЙ')))
                    counter += 1
            else:
                id_inn_field = check_admin_fields(sid, unit_id, 'ИНН')
                upd_inn_field(
                    sid,
                    unit_id,
                    id_inn_field[0],
                    str(unit.get('ИНН'))
                )
                counter += 1
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open('logging/update_inn.log', 'a') as log:
            log.write(f'Окончание импорта данных: {endtime.ctime()}\n')
            log.write(f'Ушло времени на залив данных: {delta_time}\n')
            log.write(f'Всего строк обработано: {counter} из {length}\n')
        os.remove(f'upload/{filename}')
        os.remove(f'{file_path}.json')
        with open('logging/update_inn.log', 'r') as report:
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'ГПБАЛ обновление полей ИНН', report.read())
        return redirect(url_for('fill_inn'))
    return render_template('fill_inn.html', form=form)


@app.route('/logout')
def logout():
    with open('logging/log_report.log', 'a') as report:
        user = User.query.filter_by(id=current_user.get_id()).first()
        text = f'{datetime.now().ctime()} - {user.login} - logout\n'
        report.write(text)
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/spinner', methods=['POST'])
def spinner():
    return jsonify({'data': render_template('spinner.html')})


def add_admin():
    password = os.getenv('admin_password')
    admin = User(
        login='admin',
        password=generate_password_hash(password),
        email=os.getenv('admin_email'),
        group='admin',
        access_create=True,
        access_remove=True,
        access_edit=True
    )
    db.session.add(admin)
    db.session.commit()


def add_tech_crew():
    password = os.getenv('crew_password')
    crew = User(
        login='cesar',
        password=generate_password_hash(password),
        email=os.getenv('crew_email'),
        group='cesar',
        access_create=False,
        access_remove=False,
        access_edit=False
    )
    db.session.add(crew)
    db.session.commit()


def add_carcade():
    password = os.getenv('carcade_password')
    carcade = User(
        login='carcade',
        password=generate_password_hash(password),
        email=os.getenv('carcade_email'),
        group='carcade',
        access_create=True,
        access_remove=True,
        access_edit=True
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
