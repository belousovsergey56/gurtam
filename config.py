"""Config module.

This module have all settings for Flask, SQLAlchemy, Login manager.
"""
import os

from dotenv import load_dotenv

from flask import Flask, request

from flask_bootstrap import Bootstrap

from flask_ckeditor import CKEditor

from flask_login import LoginManager, current_user

from flask_sqlalchemy import SQLAlchemy

from loguru import logger

load_dotenv()
db_password = os.getenv('mysql_password_root')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///leasing_users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
db = SQLAlchemy()
db.init_app(app)

logger.add(
    'logging/log_report.log',
    format='{time:DD-MM-YYYY HH:mm:ss} - {level} - {name} - {module} - {message}',
    rotation="60 days",
    compression="zip",
    level="INFO"
    )


def log_message(message: str) -> str:
    '''Template log message

    Args:
        ip (str): remote ip
        login (str): user login
        url (str): page opened by the user
        message (str): log message

    Return:
        str: log message in format 'ip - login - url - message'
    '''
    login = current_user.login if current_user.is_active else 'не известный',
    url = request.base_url,
    return f'{get_ip()} - {login[0]} - {url[0]} - {message}'


def get_ip() -> str:
    '''Get remote ip.

    Returns:
        str: remote ip
    '''
    return request.remote_addr
