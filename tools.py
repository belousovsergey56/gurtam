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
THIEF_MAIL = os.environ.get('thief_email')
THIEF_PASSWORD = os.environ.get('thief_password')


def send_mail(
        mail_address: str,
        subject: str,
        body: str
):
    time = datetime.now()
    tmp_message = f'Subject: {subject}\n\n{time.ctime()}\nОперация завершена:\n{body}'.encode('UTF-8')
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
        with open('logging/email_log.txt', 'a') as log:
            log.write(f'{time.ctime()}\nmsg don`t send to {mail_address}\n{e}\n\n')


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
        a = json.loads(f.read())
        return a