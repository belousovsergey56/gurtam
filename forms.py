"""Module with forms for the application."""

from flask_wtf import FlaskForm
from wtf_form import FileField, FileRequired


class UploadFile(FlaskForm):
    """Form for uploading an export file to the server.

    Args:
        FlaskForm (class): extends FlaskForm for create forms.
    """

    export_file = FileField(
        label='Загрузить файл',
        validators=[FileRequired()]
        )
