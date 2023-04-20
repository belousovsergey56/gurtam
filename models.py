# """Models data base leasing users."""
# from config import db

# from flask_login import UserMixin


# class User(UserMixin, db.Model):
#     """Data base model, User.

#     Args:
#         UserMixin (class): subclass flask login
#         db (class instance): data base instance
#     """

#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     login = db.Column(db.String(1000), unique=True)
#     password = db.Column(db.String(1000))
