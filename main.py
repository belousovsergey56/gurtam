"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""

import os
from datetime import datetime
from functools import wraps
from time import gmtime, strftime

from flask import flash, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import app, db, log_message, logger, login_manager
from constant import TOKEN, URL, lgroup
from engine import (
    check_admin_fields,
    create_object,
    fill_info,
    get_object_id,
    get_ssid,
    group_update,
    id_fields,
    upd_inn_field,
    update_object_name,
    update_param,
)
from forms import SigninForm, UploadFile, UserForm
from models import User
from tools import (
    get_diff_in_upload_file,
    is_xlsx,
    read_json,
    send_mail,
    update_bd,
    xls_to_json,
)


@login_manager.user_loader
@logger.catch
def load_user(user_id) -> User:
    """Load user to login manager.

    User manager saves data about the authorized user.

    Args:
        user_id(int): user id in data base

    Returns:
        current user
    """
    admin = User.query.filter_by(id=user_id).first()
    return admin


@logger.catch
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
            logger.info(log_message("не хватает прав для входа"))
            return render_template("403.html")
        return f(*args, **kwargs)

    return decorated_function


@app.errorhandler(401)
@logger.catch
def page_unauthorized(e):
    """401 Unauthorized.

    Page opens if user is not logged in.

    Args:
        e: response

    Returns:
        open page 401.html
    """
    logger.info(log_message("пользователь не авторизован, редирект на 401"))
    return render_template("401.html"), 401


@app.errorhandler(404)
@logger.catch
def page_not_found(e):
    """404 Not Found.

    Page opens if page note found.

    Args:
        e: response

    Returns:
        open page 404.html
    """
    logger.info(log_message("страница не найдена, редирект на 404"))
    return render_template("404.html"), 404


@app.route("/", methods=["GET", "POST"])
@logger.catch
def sign_in() -> str:
    """Sign in page.

    User authentication page.
    If an incorrect username or password is entered, an error will pop up.
    If the user is authorized, then he will be redirected to the main page
    of the application.

    Returns:
        redirect to /home page
    """
    logger.info(log_message("вход на страницу авторизации"))
    year = datetime.now().year
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if not user:
            logger.info(log_message(f"введён не верный логин {form.login.data}"))
            flash(
                message="Не верный логин,\
                попробуйте снова или обратитесть к своему администратору"
            )
            return render_template("signin.html", form=form, year=year)
        if check_password_hash(user.password, form.password.data):
            login_user(user)
            logger.info(log_message("успешная авторизация"))
            return redirect(url_for("home"))
        else:
            flash(message="Не верный пароль, попробуйте снова")
            logger.info(log_message(f"не верный пароль к логину {form.login.data}"))
            return render_template("signin.html", form=form, year=year)
    return render_template("signin.html", form=form, year=year)


@app.route("/home")
@login_required
@logger.catch
def home() -> str:
    """Home page.

    Main page with a selection menu.

    Returns:
        displays the home page of the application
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    logger.info(log_message("основная страница"))
    return render_template("index.html", user=user)


@app.route("/owners", methods=["GET", "POST"])
@login_required
@admin_only
@logger.catch
def admin():
    """Administration panel.

    Administration panel for adding, deleting users,
    updating user rights, changing passwords.

    Returns:
        render admin.html
    """
    user = User.query.filter_by(id=current_user.get_id()).first()
    logger.info(log_message("админ панель"))
    database = User.query.all()
    form = UserForm()
    return render_template("admin.html", form=form, user=user, db=database)


@app.route("/create_user", methods=["POST", "GET"])
@login_required
@logger.catch
def create_user():
    """Create user.

    Add new user and save him in data base.
    login, email, password, groups, accesses

    Returns:
        new user in DB and redirect admin.html
    """
    form = UserForm()
    leasing = User.query.filter_by(id=current_user.get_id()).first()
    logger.info(log_message("создание пользователя"))
    form.group.choices = lgroup.get(leasing.group)
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            logger.info(log_message("пользователь уже существует!!!"))
            logger.info(
                log_message(
                    f"введены данные: логин: {form.login.data}, почта: {form.email.data}, группа: {form.group.data}, права на создание: {form.access_create.data}, права на удаление: {form.access_remove.data}, права на изменение: {form.access_edit.data}"
                )
            )
            flash(
                message="""Пользователь с такой почтой уже существует,
                 попробуйте ввести новую почту"""
            )
            return redirect(url_for("create_user"))
        new_user = User(
            login=form.login.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, salt_length=13),
            group=form.group.data,
            access_create=form.access_create.data,
            access_remove=form.access_remove.data,
            access_edit=form.access_edit.data,
        )
        logger.info(log_message("пользователь успешно создан"))
        logger.info(
            log_message(
                f"введены данные: логин: {form.login.data}, почта: {form.email.data}, группа: {form.group.data},права на создание: {form.access_create.data}, права на удаление: {form.access_remove.data}, права на изменение: {form.access_edit.data}"
            )
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("create_user.html", form=form, user=leasing)


@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
@login_required
@logger.catch
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
    logger.info(log_message(f"изменение данных пользователя {edit_user.login}"))
    form = UserForm(
        login=edit_user.login,
        email=edit_user.email,
        group=edit_user.group,
        password=edit_user.password,
        access_create=edit_user.access_create,
        access_remove=edit_user.access_remove,
        access_edit=edit_user.access_edit,
    )
    form.group.choices = lgroup.get(user.group)
    if form.validate_on_submit():
        edit_user.login = form.login.data
        edit_user.email = form.email.data
        edit_user.group = form.group.data
        if user_id == user.id:
            edit_user.access_create = edit_user.access_create
            edit_user.access_remove = edit_user.access_remove
            edit_user.access_edit = edit_user.access_edit
            logger.info(
                log_message(
                    f"данные изменены: права на создание: {edit_user.access_create}, права на удаление:{edit_user.access_remove}, права на изменение: {edit_user.access_edit}"
                )
            )
        else:
            edit_user.access_create = form.access_create.data
            edit_user.access_remove = form.access_remove.data
            edit_user.access_edit = form.access_edit.data
            logger.info(
                log_message(
                    f"данные изменены: права на создание: {form.access_create.data}, права на удаление: {form.access_remove.data}, права на изменение: {form.access_edit.data}"
                )
            )
        logger.info(
            log_message(
                f"данные изменены: логин: {form.login.data}, почта: {form.email.data}, группа: {form.group.data}"
            )
        )
        db.session.commit()
        return redirect(url_for("admin"))
    return render_template("edit_user.html", form=form, user_id=edit_user.id, user=user)


@app.route("/edit_password/<int:user_id>", methods=["GET", "POST"])
@login_required
@logger.catch
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
    logger.info(log_message(f"изменение пароля пользователя: {edit_password.login}"))
    form = UserForm(
        login=edit_password.login,
        email=edit_password.email,
        group=edit_password.group,
        password=edit_password.password,
        access_create=edit_password.access_create,
        access_remove=edit_password.access_remove,
        access_edit=edit_password.access_edit,
    )
    form.group.choices = lgroup.get(user.group)
    if form.validate_on_submit():
        edit_password.password = generate_password_hash(
            form.password.data, salt_length=13
        )
        db.session.commit()
        logger.info(log_message("пароль успешно изменён"))
        return redirect(url_for("admin"))
    return render_template(
        "edit_password.html", form=form, user_id=edit_password.id, user=user
    )


@app.route("/remove_user/<int:user_id>")
@login_required
@logger.catch
def remove_user(user_id: int):
    """Remove user.

    Remove user from database.

    Args:
        user_id(int): user id to be deleted

    Returns:
        remove user from database and redirect to admin.html
    """
    teacher_to_delete = User.query.get(user_id)
    login = teacher_to_delete.login
    email = teacher_to_delete.email
    logger.info(log_message(f'пользователь "{login}" - "{email}" удалён'))
    db.session.delete(teacher_to_delete)
    db.session.commit()
    return redirect(url_for("admin"))


@app.route("/order")
@login_required
@logger.catch
def order():
    """Order page.

    This page open, when script work is done and data write in log.

    Returns:
        display order.html
    """
    logger.info(log_message("процесс завершён, редирект на страницу с отчётом"))
    logger.debug(log_message("процесс завершён, редирект на страницу с отчётом"))
    return render_template("order.html")


@app.route("/export", methods=["GET", "POST"])
@login_required
@logger.catch
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
    form = UploadFile()
    logger.info(log_message(f"экспорт на Виалон FMS {form.fms.data}"))
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        logger.info(filename)
        if not is_xlsx(filename):
            flash(message="""Ошибка импорта. Файл не в формате .XLSX""")
            logger.info(
                log_message("данные в загружаемом файле на соответсвуют формату xlsx.")
            )
            return render_template(
                "export_fms4.html", form=form, logged_in=current_user.is_authenticated
            )
        logger.info(filename)
        form.export_file.data.save("upload/{0}".format(filename))
        file_path = xls_to_json("upload/{0}".format(filename))
        import_list = read_json(file_path)
        headers = {"Инфо4", "ДЛ", "Пин"}

        if len(import_list) < 1:
            flash(message="Файл пуст")
            logger.info(log_message("Файл пустой"))
            os.remove(f"upload/{filename}")
            os.remove(f"{file_path}.json")
            return render_template(
                "export_fms4.html", form=form, logged_in=current_user.is_authenticated
            )

        for header in headers:
            if header not in import_list[0]:
                flash(
                    message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе или не соответвуют шаблону"""
                )
                logger.info(
                    log_message(
                        "данные в загружаемом файле на соответсвуют необходимому формату. Загружаемый файл удалён."
                    )
                )
                os.remove(f"upload/{filename}")
                os.remove(f"{file_path}.json")
                return render_template(
                    "export_fms4.html",
                    form=form,
                    logged_in=current_user.is_authenticated,
                )

        fms = int(form.fms.data)

        url = URL[fms]
        sid = get_ssid(url, TOKEN[fms])
        start = datetime.now()
        counter = 0
        with open(f'logging/{import_list[0].get("ЛИЗИНГ")}', "w") as log:
            log.write(f"Время начала: {start.ctime()}\n")
            log.write(f'экспорт по компании: {import_list[0].get("ЛИЗИНГ")}\n')
            log.write("Не был найден на виалон, возможно мастер не звонил:\n")
        logger.info(
            log_message(f'начало загрузки на виалон {import_list[0].get("ЛИЗИНГ")}')
        )
        for unit in import_list:
            unit_id = get_object_id(sid, unit.get("geozone_imei"), url)
            unit.update({"uid": unit_id})
            logger.info(
                log_message(f'Обновление полей объекта по ПИН {unit.get("Пин")}:{unit}')
            )
            if unit_id == -1:
                try:
                    new_id = create_object(sid, unit, url, fms)
                    unit.update({"uid": new_id})
                    update_param(sid, new_id, unit, id_fields(sid, new_id, url), url)
                    counter += 1
                except AttributeError:
                    counter += 1
            else:
                update_param(
                    sid, unit_id, unit, id_fields(sid, unit_id, url), url)
                counter += 1
        logger.info(log_message("загрузка завершена"))
        logger.info(log_message("распределение объектов по группам"))
        group_update(sid, import_list, url, fms)
        logger.info(log_message("объекты распределены"))
        logger.info(log_message("загрузка завершена"))
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open(f'logging/{import_list[0].get("ЛИЗИНГ")}', "a") as log:
            log.write(f"Время окончания: {endtime.ctime()}\n")
            log.write(f"Ушло времени на залив данных: {delta_time}\n")
            log.write(f"Обработано строк: {counter}\n")
            logger.info(log_message(f"обработано строк {counter}"))
        os.remove(f"upload/{filename}")
        os.remove(f"{file_path}.json")
        with open(f'logging/{import_list[0].get("ЛИЗИНГ")}', "r") as report:
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, "экспорт на виалон", order)
            logger.info(log_message(f'отчёт отправлен на почту "{user.email}"'))
            print(fms)
        return render_template("order.html", order=order.split("\n"))
    return render_template("export_fms4.html", form=form)


@app.route("/update_info", methods=["GET", "POST"])
@login_required
@logger.catch
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
    logger.info(log_message("обновление полей инфо Каркаде"))
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        if not is_xlsx(filename):
            flash(message="""Ошибка иморта. Файл не в формате .XLSX""")
            logger.info(
                log_message("данные в загружаемом файле на соответсвуют формату xlsx.")
            )
            return render_template(
                "update_info.html", form=form, logged_in=current_user.is_authenticated
            )
        form.export_file.data.save("upload/{0}".format(filename))
        file_path = xls_to_json("upload/{0}".format(filename))
        new_file = read_json(file_path)
        file_with_data = get_diff_in_upload_file(new_file)
        if (
            "РДДБ" not in file_with_data[0]
            and "ИНН" not in file_with_data[0]
            and "Специалист" not in file_with_data[0]
        ):
            flash(
                message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX"""
            )
            os.remove(f"upload/{filename}")
            os.remove(f"{file_path}.json")
            logger.info(log_message("данные в файле не соответсвуют формату"))
            return render_template(
                "update_info.html", form=form, logged_in=current_user.is_authenticated
            )

        fms = int(form.fms.data)

        url = URL[fms]
        sid = get_ssid(url, TOKEN[fms])
        counter = 0
        length = len(file_with_data)
        start = datetime.now()
        logger.info(log_message("старт обработки списка"))
        with open("logging/update_info.log", "w") as log:
            log.write(f"Начало загрузки: {start.ctime()}\n")
        for unit in file_with_data:
            try:
                unit_id = get_object_id(sid, unit.get("IMEI"), url)
            except TypeError:
                with open("logging/update_info.log", "a") as log:
                    log.write(f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open("logging/update_info.log", "a") as log:
                    log.write("{0} - не найден\n".format(unit.get("IMEI")))
                    counter += 1
            else:
                id_info1 = check_admin_fields(sid, unit_id, "Инфо1", url)
                id_info5 = check_admin_fields(sid, unit_id, "Инфо5", url)
                id_info6 = check_admin_fields(sid, unit_id, "Инфо6", url)
                id_info7 = check_admin_fields(sid, unit_id, "Инфо7", url)
                id_value_list = [id_info1, id_info5, id_info6, id_info7]
                fill_info(sid, unit_id, id_value_list, unit, url)
                logger.info(log_message(f'{unit.get("IMEI")} - {id_value_list}'))
                logger.debug(f"Готово {round(counter / length*100, 2)} %")
                counter += 1
        endtime = datetime.now()
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        logger.info(log_message("обновление полей инфо завершено"))
        with open("logging/update_info.log", "a") as log:
            log.write(f"Окончание экспорта данных: {endtime.ctime()}\n")
            log.write(f"Ушло времени на залив данных: {delta_time}\n")
            log.write(f"Всего строк обработано: {counter} из {length}\n")
            logger.info(log_message(f"обработано строк {counter} из {length}"))
        update_bd(new_file)
        os.remove(f"upload/{filename}")
        os.remove(f"{file_path}.json")
        with open("logging/update_info.log", "r") as report:
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, "РДДБ обновление полей ИНФО", order)
            logger.info(log_message(f'отчёт отправлен на почту "{user.email}"'))
        return render_template("order.html", order=order.split("\n"))
    return render_template("update_info.html", form=form)


@app.route("/fill_inn", methods=["GET", "POST"])
@login_required
@logger.catch
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
    logger.info(log_message("обновить поле ИНН ГПБАЛ"))
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        if not is_xlsx(filename):
            flash(message="""Ошибка иморта. Файл не в формате .XLSX""")
            logger.info(
                log_message("данные в загружаемом файле на соответсвуют формату xlsx.")
            )
            return render_template(
                "fill_inn.html", form=form, logged_in=current_user.is_authenticated
            )
        form.export_file.data.save("upload/{0}".format(filename))
        file_path = xls_to_json("upload/{0}".format(filename))
        new_file = read_json(file_path)
        if "ИНН" not in new_file[0] and "IMEI" not in new_file[0]:
            flash(
                message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX"""
            )
            os.remove(f"upload/{filename}")
            os.remove(f"{file_path}.json")
            logger.info(log_message("данные в файле не соответвуют формату"))
            return render_template(
                "fill_inn.html", form=form, logged_in=current_user.is_authenticated
            )
        fms = int(form.fms.data)

        url = URL[fms]
        sid = get_ssid(url, TOKEN[fms])
        counter = 0
        length = len(new_file)
        start = datetime.now()
        logger.info(log_message("старт обновления полей ИНН"))
        with open("logging/update_inn.log", "w") as log:
            log.write(f"Начало загрузки: {start.ctime()}\n")
        for unit in new_file:
            try:
                unit_id = get_object_id(sid, int(unit.get("IMEI")), url)
            except TypeError:
                with open("logging/update_inn.log", "a") as log:
                    print("except but have ifelse bloco..")
                    log.write(f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open("logging/update_inn.log", "a") as log:
                    log.write("{0} - не найден\n".format(unit.get("ИМЕЙ")))
                    counter += 1
            else:
                id_inn_field = check_admin_fields(sid, unit_id, "ИНН", url)
                upd_inn_field(sid, unit_id, id_inn_field[0], unit.get("ИНН"), url)
                counter += 1
                logger.info(log_message(f'{unit.get("IMEI")} - {unit.get("ИНН")}'))
        endtime = datetime.now()
        logger.info(log_message("обновление ИНН завершено"))
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open("logging/update_inn.log", "a") as log:
            log.write(f"Окончание экспорта данных: {endtime.ctime()}\n")
            log.write(f"Ушло времени на залив данных: {delta_time}\n")
            log.write(f"Всего строк обработано: {counter} из {length}\n")
            logger.info(log_message(f"обработано строк {counter} из {length}"))
        os.remove(f"upload/{filename}")
        os.remove(f"{file_path}.json")
        with open("logging/update_inn.log", "r") as report:
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, "ГПБАЛ обновление полей ИНН", order)
            logger.info(log_message(f'отчёт отправлен на почту "{user.email}"'))
        return render_template("order.html", order=order.split("\n"))
    return render_template("fill_inn.html", form=form)


@app.route("/rename_object", methods=["GET", "POST"])
@login_required
@logger.catch
def update_name():
    """Rename a list of objects
    The page displays information explaining what extension is required for
    the file, what headers and data the file should contain.
    Contains a form for uploading a file and an 'Export' button.
    The server receives the file and processes it, as a result of which the
    object name on the vialon is changed to the corresponding one from the
    file.
    After processing, a report on the number of rows processed will be
    displayed on the page.
    If there are errors, objects not found, for example,
    then the report will contain a list of not found objects.
    """
    logger.info(log_message("Массовое переименовывание объектов"))
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        if not is_xlsx(filename):
            flash(message="""Ошибка иморта. Файл не в формате .XLSX""")
            logger.info(
                log_message("данные в загружаемом файле на соответсвуют формату xlsx.")
            )
            return render_template(
                "rename_objects.html", form=form, logged_in=current_user.is_authenticated
            )
        form.export_file.data.save("upload/{0}".format(filename))
        file_path = xls_to_json("upload/{0}".format(filename))
        new_file = read_json(file_path)
        if "ДЛ" not in new_file[0] and "IMEI" not in new_file[0]:
            flash(
                message="""Ошибка иморта. Необходимые данные не находятся на
             первом листе, не соответвуют шаблону или не в формате .XLSX"""
            )
            os.remove(f"upload/{filename}")
            os.remove(f"{file_path}.json")
            logger.info(log_message("данные в файле не соответвуют формату"))
            return render_template(
                "rename_objects.html", form=form, logged_in=current_user.is_authenticated
            )
        fms = int(form.fms.data)

        url = URL[fms]
        sid = get_ssid(url, TOKEN[fms])
        counter = 0
        length = len(new_file)
        start = datetime.now()
        logger.info(log_message("старт обновления полей ДЛ"))
        with open("logging/rename_objects.log", "w") as log:
            log.write(f"Начало загрузки: {start.ctime()}\n")
        for unit in new_file:
            try:
                unit_id = get_object_id(sid, int(unit.get("IMEI")), url)
            except TypeError:
                with open("logging/rename_objects.log", "a") as log:
                    log.write(f'{unit.get("IMEI")} не верный формат или не найден')
                continue
            if unit_id == -1:
                with open("logging/rename_objects.log", "a") as log:
                    log.write("{0} - не найден\n".format(unit.get("IMEI")))
                    counter += 1
            else:
                update_object_name(sid, url, unit_id, unit.get("ДЛ"))
                counter += 1
                logger.info(
                    log_message(
                        f'Новое имя для {unit.get("IMEI")} - {unit.get("ДЛ")}'))
        endtime = datetime.now()
        logger.info(log_message("обновление ДЛ завершено"))
        delta_time = endtime - start
        delta_time = strftime("%H:%M:%S", gmtime(delta_time.total_seconds()))
        with open("logging/rename_objects.log", "a") as log:
            log.write(f"Окончание экспорта данных: {endtime.ctime()}\n")
            log.write(f"Ушло времени на залив данных: {delta_time}\n")
            log.write(f"Всего строк обработано: {counter} из {length}\n")
            logger.info(log_message(f"обработано строк {counter} из {length}"))
        os.remove(f"upload/{filename}")
        os.remove(f"{file_path}.json")
        with open("logging/rename_objects.log", "r") as report:
            order = report.read()
            user = User.query.filter_by(id=current_user.get_id()).first()
            send_mail(user.email, "Массовое переименование объектов", order)
            logger.info(
                log_message(f'отчёт отправлен на почту "{user.email}"'))
        return render_template("order.html", order=order.split("\n"))
    return render_template("rename_objects.html", form=form)


@app.route("/logout")
@login_required
def logout():
    """User logout.

    When a user clicks the "Выход" button, the login manager removes
    the user from the pool of active sessions.
    And redirects to the authentication page.

    Returns:
        redirects to the authentication page
    """
    logger.info(log_message(f'пользователь "{current_user.login}" вышел'))
    logout_user()
    return redirect(url_for("sign_in"))


@app.route("/spinner", methods=["POST"])
def spinner():
    """Spinner.

    A pop-up window with a spinner to let the user understand that the process
    is running and the data is being updated on the wialon server.
    """
    logger.debug("старт спиннера")
    return jsonify({"data": render_template("spinner.html")})


def add_admin() -> None:
    """Add user admin in data base."""
    password = os.getenv("admin_password")
    admin = User(
        login="admin",
        password=generate_password_hash(password),
        email=os.getenv("admin_email"),
        group="admin",
        access_create=True,
        access_remove=True,
        access_edit=True,
    )
    logger.debug(
        f"создание учётки админа - login: {admin.login}, email: {admin.email}, группа: {admin.group}, полный доступ на чтение, создание, удаление"
    )
    db.session.add(admin)
    db.session.commit()


def add_tech_crew() -> None:
    """Add user tech team in data base."""
    password = os.getenv("crew_password")
    crew = User(
        login="cesar",
        password=generate_password_hash(password),
        email=os.getenv("crew_email"),
        group="cesar",
        access_create=False,
        access_remove=False,
        access_edit=False,
    )
    logger.debug(
        f"создание учётки отдела - login: {crew.login}, email: {crew.email}, группа: {crew.group}, доступ к адмике отсутвует"
    )
    db.session.add(crew)
    db.session.commit()


def add_carcade():
    """Add user carcade in data base."""
    password = os.getenv("carcade_password")
    carcade = User(
        login="carcade",
        password=generate_password_hash(password),
        email=os.getenv("carcade_email"),
        group="carcade",
        access_create=True,
        access_remove=True,
        access_edit=True,
    )
    logger.debug(
        f"создание учётки Каркаде - login: {carcade.login}, email: {carcade.email}, группа: {carcade.group}, полный доступ на чтение, создание, удаление"
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

if __name__ == "__main__":
    logger.info(f"запуск сервера {app}")
    app.run(host="0.0.0.0", port=5000)
    logger.info("сервер остановлен")
