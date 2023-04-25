"""Config module.

This module have all settings for Flask, SQLAlchemy, Login manager.
"""
import os

from dotenv import load_dotenv

from flask import Flask

from flask_bootstrap import Bootstrap

from flask_ckeditor import CKEditor

from flask_login import LoginManager

from flask_sqlalchemy import SQLAlchemy


load_dotenv()
db_password = os.getenv('mysql_password_root')


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Bootstrap(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///leasing_users.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

login_manager = LoginManager()
login_manager.init_app(app)
ckeditor = CKEditor(app)
db = SQLAlchemy()
db.init_app(app)
