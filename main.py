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
from gurtam import check_admin_fields
from gurtam import update_param
from gurtam import fill_info, upd_inn_field
from gurtam import get_admin_fields, get_custom_fields
from gurtam import create_admin_field, create_custom_field

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
def load_user(user_id) -> User:
    """Load user to login manager.

    User manager saves data about the authorized user.

    Args:
        user_id(int): user id in data base

    Returns:
        current user
    """
    return User.query.filter_by(id=user_id).first()


def admin_only(f) -> str:
    """Decorator, admin validator.

    If the page is opened by a non-administrator,
    the user is redirected to a 403 page.

    Returns:
        page 403: 403.html
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.get_id() != str(1):
            return render_template('403.html')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def sign_in() -> str:
    """Sign in page.

    User authentication page.
    If an incorrect username or password is entered, an error will pop up.
    If the user is authorized, then he will be redirected to the main page
    of the application.

    Returns:
        redirect to /home page
    """
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
    """Home page.

    Main page with a selection menu.

    Returns:
        displays the home page of the application
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
    """Administration panel.

    Administration panel for adding, deleting users,
    updating user rights, changing passwords.

    Returns:
        render admin.html
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    database = User.query.all()
    form = UserForm()
    return render_template('admin.html', form=form, user=user, db=database)


@app.route('/create_user', methods=['POST', 'GET'])
@login_required
def create_user():
    """Create user.

    Add new user and save him in data base.
    login, email, password, groups, accesses

    Returns:
        new user in DB and redirect admin.html
    """
    form = UserForm()
    leasing = User.query.filter_by(id=current_user.get_id()).first()

    form.group.choices = lgroup.get(leasing.group)
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(
                message="""Пользователь с такой почтой уже существует,
                 попробуйте ввести новую почту""")
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
    """Edit user.

    Edit user name, email, group.
    Page have a link to change password.

    Args:
        user_id(int): ID of the user to whom the data is being updated

    Returns:
        update user data and redirect to admin.html
    """
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
    """Edit password.

    Edit user password.

    Args:
        user_id(int): ID of the user to whom the data is being updated

    Returns:
        update user data and redirect to admin.html
    """
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
    """Remove user.

    Remove user from database.

    Args:
        user_id(int): user id to be deleted

    Returns:
        remove user from database and redirect to admin.html
    """
    teacher_to_delete = User.query.get(user_id)
    db.session.delete(teacher_to_delete)
    db.session.commit()
    return redirect(url_for('admin'))


def id_fields(sid, new_id) -> dict:
    """Get id fields.

    Helper function.
    Create map id fields.
    Search field id and add to dict.
    Search custom and admin fields.
    If id field not found, go to create field and add new id to dict.
    Them return dict with field name and current id.
    Current name and id:
    geozone_sim, geozone_imei, Vin, Марка, Модель, Пин, Инфо4

    Args:
        sid (str): current session id
        new_id: integer unit/object id

    Returns:
        map_id (dict): dict with current field name and field id
    """
    admin_fields = get_admin_fields(sid, new_id)
    custom_fields = get_custom_fields(sid, new_id)
    map_id = {
        'geozone_imei': None,
        'geozone_sim': None,
        'Vin': None,
        'Марка': None,
        'Модель': None,
        'Пин': None,
        'Инфо4': None
    }
    for field in admin_fields.items():
        name_field = field[1].get('n')
        id_field = field[1].get('id')
        if name_field in map_id.keys():
            map_id.update({name_field: id_field})

    for field in custom_fields.items():
        name_field = field[1].get('n')
        id_field = field[1].get('id')
        if name_field in map_id.keys():
            map_id.update({name_field: id_field})

    for names, values in map_id.items():
        if values is None:
            if names == 'Vin' or names == 'Марка' or names == 'Модель':
                field = create_custom_field(sid, new_id, names)
                map_id.update({names: field[1].get('id')})
            else:
                field = create_admin_field(sid, new_id, names)
                map_id.update({names: field[1].get('id')})
    return map_id


@app.route('/order')
@login_required
def order():
    """Order page.

    This page open, when script work is done and data write in log.

    Returns:
        display order.html
    """
    return render_template('order.html')


@app.route('/export', methods=['GET', 'POST'])
@login_required
def export_fms4():
    """Import object data to Wialon.

    Page displays a field for uploading an excel file and
    buttons for sending the file for processing.
    Right there, just below the form, there is a description field
    with a hint about which file can and should be uploaded here.
    The function will convert the excel file into json then into a dictionary.
    The function checks if the file is suitable for processing by the main
    script, if not, then it reports an error to the user.
    Next, the data from the dictionary is uploaded to the wialon server.
    When the download is completed, the user will be redirected to a page with
    a report on the data upload to the server.
    At the same time, the user will receive an email with the same report.

    Returns:
        display page export_fms4.html
    """
    with open('logging/log_report.log', 'a') as report:
        user = User.query.filter_by(id=current_user.get_id()).first()
        text = f"""{datetime.now().ctime()} - {user.login} - open page import
         on fms4\n"""
        report.write(text)
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        import_list = read_json(file_path)
        if """Инфо4
        """ not in import_list[0] and """ДЛ
        """ not in import_list[0] and """Пин""" not in import_list[0]:
            flash(message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX""")
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
            log.write(f'Импорт по компании: {import_list[0].get("ЛИЗИНГ")}\n')
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
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'Импорт на виалон', order)
        return render_template('order.html', order=order.split('\n'))
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
        display page remove_groups.html
    """
    form = UploadFile()

    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        imei_list = read_json(file_path)

        if 'ГРУППА' not in imei_list[0] and 'ИМЕЙ' not in imei_list[0]:
            flash(message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX""")
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
            log.write(f"""\nУдаление объектов из группы по маске
             - {imei_list[0].get("ГРУППА")}\n""")
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
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'Удаление объектов из групп', order)
        return render_template('order.html', order=order.split('\n'))
    return render_template('remove_groups.html', form=form)


@app.route('/update_info', methods=['GET', 'POST'])
@login_required
def update_info():
    """Carcade, update info fields.

    Page update info display field for upload current xlsx file.
    If file is not correct, popup error text.
    First, the uploaded file is compared with the current state of the
    database, the snapshot of the database is stored on the server in json
    format.
    The data is updated in such fields as Info1, Info5, Info6, Info7.
    Where Инфо1 - РДДБ, Инфо5 - Специалист, Инфо6 - ИНН, Инфо7 - КПП.
    When the download is complete, the user will be redirected to the page
    with the report and the script will be sent. In parallel with this, the
    script will send a letter to the user with the same report.

    Returns:
        display update_info.html then the report page order.html
    """
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        new_file = read_json(file_path)
        file_with_data = get_diff_in_upload_file(new_file)
        if """РДДБ
        """ not in file_with_data[0] and """ИНН
        """ not in file_with_data[0] and """Специалист
        """ not in file_with_data[0]:
            flash(message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX""")
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
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'РДДБ обновление полей ИНФО', order)
        return render_template('order.html', order=order.split('\n'))
    return render_template('update_info.html', form=form)


@app.route('/fill_inn', methods=['GET', 'POST'])
def fill_inn():
    """GPBL, fill field INN.

    Page update info display field for upload current xlsx file.
    If file is not correct, pop up error text.
    The data is create and updated field ИНН.
    When the download is complete, the user will be redirected to the page
    with the report and the script will be sent. In parallel with this, the
    script will send a letter to the user with the same report.

    Returns:
        display fill_inn.html then the report page order.html
    """
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        file_path = xls_to_json('upload/{0}'.format(filename))
        new_file = read_json(file_path)
        if 'ИНН' not in new_file[0] and 'IMEI' not in new_file[0]:
            flash(message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX""")
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
                    log.write('{0} - не найден\n'.format(unit.get('ИМЕЙ')))
                    counter += 1
            else:
                id_inn_field = check_admin_fields(sid, unit_id, 'ИНН')
                upd_inn_field(
                    sid,
                    unit_id,
                    id_inn_field[0],
                    unit.get('ИНН')
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
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, 'ГПБАЛ обновление полей ИНН', order)
        return render_template('order.html', order=order.split('\n'))
    return render_template('fill_inn.html', form=form)


@app.route('/logout')
def logout():
    """User logout.

    When a user clicks the "Выход" button, the login manager removes
    the user from the pool of active sessions.
    And redirects to the authentication page.

    Returns:
        redirects to the authentication page
    """
    with open('logging/log_report.log', 'a') as report:
        user = User.query.filter_by(id=current_user.get_id()).first()
        text = f'{datetime.now().ctime()} - {user.login} - logout\n'
        report.write(text)
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/spinner', methods=['POST'])
def spinner():
    """Spinner.

    A pop-up window with a spinner to let the user understand that the process
    is running and the data is being updated on the wialon server.
    """
    return jsonify({'data': render_template('spinner.html')})


def add_admin() -> None:
    """Add user admin in data base."""
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


def add_tech_crew() -> None:
    """Add user tech team in data base."""
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
    """Add user carcade in data base."""
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
