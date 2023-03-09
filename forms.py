"""Module with forms for the application."""

from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired


class UploadFile(FlaskForm):
    """Form for uploading an export file to the server.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    export_file = FileField(validators=[DataRequired()])
    submit = SubmitField('Экспорт')
