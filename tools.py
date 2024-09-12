"""Additional tools module.

This module contains such functions as:
sending email, reading xlsx file and reading json into a dictionary,
file comparison and snapshot of the latest wialon database state etc.
"""

import json
import os
import smtplib
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from config import fstart_stop, logger

load_dotenv()

HOSTING_EMAIL = os.environ.get("hosting_email")
HOSTING_LOIGN = os.environ.get("hosting_login")
HOSTING_EMAIL_PASSWORD = os.environ.get("hosting_email_password")
SMTP_HOST = os.environ.get("smtp_host")


@fstart_stop
@logger.catch
def send_mail(mail_address: str, subject: str, body: str) -> None:
    """Send email.

    The function of sending e-mails from the spb.csat.ru host
    to the mail of an authorized user.

    Args:
        mail_address(str): Email address of the recipient
        subject(str): Email Subject
        body(str): Email Body
    """
    time = datetime.now()
    tmp_message = (
        f"Subject: {subject}\n\n{time.ctime()}\nОперация завершена:\n{body}".encode("UTF-8")
    )
    logger.debug("Отправка элетронного письма")
    logger.debug(f"Кому: {mail_address}")
    logger.debug(f"Тема: {subject}")
    logger.debug(f"Текст письма: {body}")
    try:
        with smtplib.SMTP(host=SMTP_HOST, port=587) as connection:
            connection.starttls()
            connection.login(
                user=HOSTING_LOIGN, password=HOSTING_EMAIL_PASSWORD)
            connection.sendmail(
                from_addr=HOSTING_EMAIL, to_addrs=mail_address, msg=tmp_message
            )
        logger.debug(f"user: {HOSTING_LOIGN}")
        logger.debug(f"mail: {HOSTING_EMAIL}")
    except smtplib.SMTPException as e:
        with open("logging/email_log.log", "a") as log:
            log.write(f"{time.ctime()}\nmsg don`t send to {mail_address}\n{e}\n\n")
        logger.error(f"Письмо на адрес {mail_address} не отправлено")
        logger.debug(e)


@fstart_stop
@logger.catch
def xls_to_json(xls_file) -> str:
    """Convert Excel file to json.

    Args:
        xls_file (file.xlsx): Excel file to be converted to json

    Returns:
        path(str): path of the json file
    """
    logger.info("Файл на входе:")
    logger.info(str(xls_file))
    new_file_name = f"{xls_file}".replace(".xlsx", "")
    logger.debug(f"Убрать расширение - {new_file_name}")
    xls = pd.read_excel(xls_file, dtype=str)
    logger.debug(f"Чтение файла Пандас - {xls}")
    xls.to_json(f"{new_file_name}.json", orient="records")
    logger.debug(f"Преобразованный файл в json - {new_file_name}")
    return new_file_name


@fstart_stop
@logger.catch
def is_xlsx(input_file) -> bool:
    logger.debug(f"Проверка {input_file} на наличие расширения xlsx")
    if "xlsx" not in input_file:
        logger.debug("Расширение не соответсвует")
        return False
    logger.debug("Расширение соответсвует")
    return True


@fstart_stop
@logger.catch
def read_json(file_path) -> dict:
    """Read a file.

    The function reads a json file saved in upload/ directory
    and returns a dictionary.

    Returns:
        dict: dictionary ready to use
    """
    logger.info("Файл на входе:")
    logger.info(f"{file_path}")
    with open(f"{file_path}.json", "r", encoding="UTF-8") as f:
        json_file = json.loads(f.read())
        logger.debug(f"Файл преобразованный в json формат - {json_file}")
        return json_file


@fstart_stop
@logger.catch
def get_headers(json_file: dict) -> list[str]:
    """Get column headers.

    Args:
        json_file(dict): dictionary with data

    Returns:
        headers(list): title list
    """
    logger.debug("Файл на входе:")
    data_frame = pd.DataFrame(json_file)
    headers = data_frame.columns.values.tolist()
    logger.debug(f"Получение заголовков файла - {headers}")
    return headers


@fstart_stop
@logger.catch
def update_bd(data: list[dict]) -> None:
    """Get snapshot carcade data.

    The function reads the incoming carcade file and saves the data
    to a separate json file.
    """
    logger.debug(f"На входе функции словарь - {data}")
    bd = {}
    for value in data:
        imei = None
        inn = None
        if type(value.get("IMEI")) is float:
            imei = int(value.get("IMEI"))
            logger.debug("Если ИМЕЙ float, преобразуем в integer")
        else:
            imei = value.get("IMEI")
        if type(value.get("ИНН")) is float:
            inn = int(value.get("ИНН"))
            logger.debug("Если ИНН float, преобразуем в integer")
        else:
            inn = value.get("ИНН")
        bd.update(
            {
                imei: {
                    "РДДБ": value.get("РДДБ"),
                    "Специалист": value.get("Специалист"),
                    "IMEI": imei,
                    "ИНН": inn,
                    "КПП": value.get("КПП"),
                }
            }
        )
        logger.debug("Снимок базы данных каркаде готов")
        logger.debug('Записан в файл "data_carcade/last_db.json"')
    with open("data_carcade/last_db.json", "w") as f:
        json.dump(bd, f, ensure_ascii=False)


@fstart_stop
@logger.catch
def get_diff_in_upload_file(new_file: list[dict]) -> list[dict]:
    """Comparing an input file with a snapshot.

    The function compares the data from the input file with the data stored
    since the last update and returns a list of objects that do not exist or
    have changed relative to the snapshot.

    Args:
        new_file(list[dict]): incoming data

    Returns:
        to_update(list[dict]): data to be added or changed on wialon server
    """
    logger.debug("На входе функции свежий словарь с объектам Каркаде")
    to_update = []
    last_db = read_json("data_carcade/last_db")
    for value in new_file:
        imei = str(value.get("IMEI"))
        inn = None
        if type(value.get("ИНН")) is float:
            inn = int(value.get("ИНН"))
        else:
            inn = value.get("ИНН")
        if imei in last_db:
            if (
                value.get("РДДБ") != last_db[imei].get("РДДБ")
                or value.get("Специалист") != last_db[imei].get("Специалист")
                or inn != last_db[imei].get("ИНН")
                or value.get("КПП") != last_db[imei].get("КПП")
            ):
                last_db[imei].update(value)
                to_update.append(value)
        else:
            to_update.append(value)
    logger.debug(
        "Если данные между локальной базой и входящей хотя бы в одном поле отлиачются, данный объект записывается в новый список словарей, который и возращает функция т.о из более 15к строк, новый список объектов содержит только актуальные значения, в среднем от 200 до 600 объектов."
    )
    return to_update


def __json_to_xlsx(path: str) -> None:
    """Convert json to xls

    Args:
        path (str): path to file
    """
    name = path.split('.')[0]
    data = pd.read_json(path)
    data.to_excel(f'{name}.xlsx', index=False)
