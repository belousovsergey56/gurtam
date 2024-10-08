"""Module with forms for the application."""

from constant import FMS
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    FileField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired


class UploadFile(FlaskForm):
    """Form for uploading an export file to the server.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    fms = SelectField(label="", render_kw={"placeholder": "FMS"}, choices=FMS)
    export_file = FileField(validators=[DataRequired()])
    submit = SubmitField("Экспорт")


class SigninForm(FlaskForm):
    """Sign in form.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    login = StringField(
        label="",
        render_kw={"placeholder": "Логин"},
        validators=[
            DataRequired(),
        ],
    )
    password = PasswordField(
        label="",
        render_kw={"placeholder": "Пароль"},
        validators=[
            DataRequired(),
        ],
    )
    submit = SubmitField("Войти")


class UserForm(FlaskForm):
    """User in form.

    Function form for user management in the admin panel.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    login = StringField(
        label="",
        render_kw={"placeholder": "Логин"},
        validators=[
            DataRequired(),
        ],
    )
    email = EmailField(
        label="",
        render_kw={"placeholder": "Адрес электронной почты"},
        validators=[DataRequired()],
    )
    password = PasswordField(
        label="",
        render_kw={"placeholder": "Пароль"},
        validators=[
            DataRequired(),
        ],
    )
    group = SelectField(label="", render_kw={"placeholder": "Выбрать лизинг"})
    access_create = BooleanField(label="Создание")
    access_remove = BooleanField(label="Удаление")
    access_edit = BooleanField(label="Изменение")
