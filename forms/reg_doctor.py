from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField, FileField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError


class RegistraionDoctorForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    surname = StringField('Фамилимя', validators=[DataRequired()])
    img_picker = FileField('Изображение (Необязательно)')
    prof = StringField('Специальность врача', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')