from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField, FileField, Field
from wtforms.validators import DataRequired, Email, InputRequired, Length, ValidationError


class Change_Btns(FlaskForm):
    edit = SubmitField('редактировать')
    delete = SubmitField('удалить')
    id = IntegerField('ID', render_kw={'readonly': True})