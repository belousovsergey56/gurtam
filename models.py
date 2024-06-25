"""Models data base leasing users."""
from flask_login import UserMixin

from config import app, db


class User(UserMixin, db.Model):
    """Data base model, User.

    Two fields: login, email, password, group and three fields for access

    Args:
        UserMixin (class): subclass flask login
        db (class instance): data base instance
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(1000))
    email = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(1000))
    group = db.Column(db.String(100))
    access_create = db.Column(db.Boolean)
    access_remove = db.Column(db.Boolean)
    access_edit = db.Column(db.Boolean)


with app.app_context():
    db.create_all()
