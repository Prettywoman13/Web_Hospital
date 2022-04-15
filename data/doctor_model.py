import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Reg_Doctor(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'reg_doctor'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, index=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    middle_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    prof = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    image = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True, default=None)
    is_active = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    doc_schedule = orm.relation("Schedule", back_populates='doctor')

    def set_hash_psw(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Schedule(SqlAlchemyBase):
    __tablename__ = 'add_schedule'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    doc_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("reg_doctor.id"), nullable=False)
    doctor = orm.relation('Reg_Doctor')
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    tickets = sqlalchemy.Column(sqlalchemy.TIME, nullable=False)
    state = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    sch = orm.relation("ScheduleForUser", back_populates='user_ticket')


class ScheduleForUser(SqlAlchemyBase):
    __tablename__ = 'schedule_for_user'
    __table_args__ = {'extend_existing': True}
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    schedule_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("add_schedule.id"), nullable=False)
    user_ticket = orm.relation('Schedule')
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("reg_users.id"), nullable=False)





