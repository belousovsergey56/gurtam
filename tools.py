import json

import os

import pandas as pd

import smtplib

import ssl

from datetime import datetime

from dotenv import load_dotenv


load_dotenv()

HOSTING_EMAIL = os.environ.get('hosting_email')
HOSTING_LOIGN = os.environ.get('hosting_login')
HOSTING_EMAIL_PASSWORD = os.environ.get('hosting_email_password')


def send_mail(
        mail_address: str,
        subject: str,
        body: str
):
    time = datetime.now()
    tmp_message = f'Subject: {subject}\n\n{time.ctime()}\nОперация завершена:\n{body}'.encode(
        'UTF-8')
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(host='smtp.spb.csat.ru', context=context, port=465) as connection:
            connection.login(
                user=HOSTING_LOIGN,
                password=HOSTING_EMAIL_PASSWORD
            )
            connection.sendmail(
                from_addr=HOSTING_EMAIL,
                to_addrs=mail_address,
                msg=tmp_message
            )
    except smtplib.SMTPException as e:
        with open('logging/email_log.log', 'a') as log:
            log.write(
                f'{time.ctime()}\nmsg don`t send to {mail_address}\n{e}\n\n')


def xls_to_json(xls_file):
    """Convert Excel file to json.

    Args:
        xls_file (file.xlsx): Excel file to be converted to json
    """
    new_file_name = f'{xls_file}'.replace('.xlsx', '')
    xls = pd.read_excel(xls_file)
    xls.to_json(f'{new_file_name}.json', orient='records')
    return new_file_name


def read_json(file_path) -> dict:
    """Read a file.

    The function reads a json file saved in upload/ directory
    and returns a dictionary.

    Returns:
        dict: dictionary ready to use
    """
    with open(f'{file_path}.json', 'r', encoding='UTF-8') as f:
        json_file = json.loads(f.read())
        return json_file


def inn_to_int(incoming_file: dict, field_name: str) -> None:
    for inn_value in incoming_file:
        if type(inn_value.get(field_name)) is float:
            inn_value.update({field_name: int(inn_value.get(field_name))})


def update_bd(data: list[dict]) -> None:
    bd = {}
    for value in data:
        imei = None
        inn = None
        if type(value.get("IMEI")) == float:
            imei = int(value.get("IMEI"))
        else:
            imei = value.get("IMEI")
        if type(value.get("ИНН")) == float:
            inn = int(value.get("ИНН"))
        else:
            inn = value.get("ИНН")
        bd.update(
            {
                imei: {
                    "РДДБ": value.get('РДДБ'),
                    "Специалист": value.get('Специалист'),
                    "IMEI": imei,
                    "ИНН": inn,
                    "КПП": value.get('КПП')
                }
            })
    with open('data_carcade/last_db.json', 'w') as f:
        json.dump(bd, f, ensure_ascii=False)


def get_diff_in_upload_file(new_file: list[dict]) -> list[dict]:
    to_update = []
    last_db = read_json('data_carcade/last_db')
    for value in new_file:
        imei = str(value.get("IMEI"))
        inn = None
        if type(value.get("ИНН")) == float:
            inn = int(value.get("ИНН"))
        else:
            inn = value.get("ИНН")
        if imei in last_db:
            if value.get("РДДБ") != last_db[imei].get("РДДБ") or\
                    value.get("Специалист") != last_db[imei].get("Специалист") or\
                    inn != last_db[imei].get("ИНН") or\
                    value.get("КПП") != last_db[imei].get("КПП"):
                last_db[imei].update(value)
                to_update.append(value)
        else:
            to_update.append(value)
    return to_update
