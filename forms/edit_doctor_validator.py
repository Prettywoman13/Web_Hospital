from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError


class ChangeDoctorForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    surname = StringField('Фамилимя', validators=[DataRequired()])
    img_picker = FileField('Изображение (Необязательно)')
    prof = StringField('Специальность врача', validators=[DataRequired()])
    is_active = BooleanField('Активировать врача')
    submit = SubmitField('Изменить данные')