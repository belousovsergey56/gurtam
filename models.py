"""Models data base leasing users."""
from config import app, db, admin
from flask_admin.contrib.sqla import ModelView

from werkzeug.security import generate_password_hash

from flask_login import UserMixin


class User(UserMixin, db.Model):
    """Data base model, User.

    Two fields: login, password

    Args:
        UserMixin (class): subclass flask login
        db (class instance): data base instance
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(1000))
    email = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(1000))

    def __init__(self, login, email, password):
        self.login = login
        self.email = email
        self.password = password


class AdminView(ModelView):
    def on_model_change(self, form, model, is_created):
        if 'password' in form:
            model.password = generate_password_hash(form.password.data)
        super(AdminView, self).on_model_change(form, model, is_created)
    form_widget_args = {
        'password': {'type': 'password'}
    }


admin.add_view(AdminView(User, db.session))

with app.app_context():
    db.create_all()
