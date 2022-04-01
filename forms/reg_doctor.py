from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError


class RegistraionDoctorForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    surname = StringField('Фамилимя', validators=[DataRequired()])
    prof = StringField('Специальность врача', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')