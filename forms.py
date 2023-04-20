"""Module with forms for the application."""

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired


class UploadFile(FlaskForm):
    """Form for uploading an export file to the server.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    export_file = FileField(validators=[DataRequired()])
    submit = SubmitField('Экспорт')


class SigninForm(FlaskForm):
    """Sign in form.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    email = TextAreaField(
        label='',
        render_kw={'placeholder': 'Логин'},
        validators=[DataRequired()]
    )
    password = PasswordField(
        label='',
        render_kw={'placeholder': 'Пароль'},
        validators=[DataRequired()]
    )
    submit = SubmitField('Войти')
