import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Reg_User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'reg_users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    patronymic = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    pnone_number = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    snils = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    oms_series = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    oms_number = sqlalchemy.Column(sqlalchemy.String, nullable=False)


    def set_hash_psw(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_name(self):
        return self.name