"""Main module.

This module, have main method.
Run browser and run all project for export data object to Gurtam.
"""
from flask import Flask, render_template, url_for, redirect
from gurtam import add_groups, update_param, get_ssid
from read_file import xls_to_json, read_json
from forms import UploadFile
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


@app.route('/')
def home() -> str:
    """Render home page.

    Returns:
        str: displays the home page of the application
    """
    return render_template('index.html')


@app.route('/export', methods=['GET', 'POST'])
def export_fms4():
    form = UploadFile()
    if form.validate_on_submit():
        filename = secure_filename(form.export_file.data.filename)
        form.export_file.data.save('upload/{0}'.format(filename))
        # form.export_file.data.save('upload/raw.xlsx')
        # xls_to_json('upload/raw.xlsx')
        return redirect(url_for('export_fms4'))
    return render_template('export_fms4.html', form=form)


@app.route('/remove_groups', methods=['GET', 'POST'])
def remove_groups():
    return render_template('remove_groups.html')


if __name__ == '__main__':
    os.system('xdg-open http://127.0.0.1:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)
