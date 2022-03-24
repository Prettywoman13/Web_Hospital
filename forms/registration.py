from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField
from wtforms.validators import DataRequired, Email, InputRequired, Length


class RegistraionForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_rep = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    snils = IntegerField('СНИЛС', validators=[DataRequired(), Length(min=11, max=11)])
    number_phone = IntegerField('Номер телефона', validators=[DataRequired()])
    series_oms = IntegerField('Серия полиса ОМС (необязательно)', validators=[DataRequired()])
    number_oms = IntegerField('Номер полиса ОМС', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')

