from flask_wtf import FlaskForm
from wtforms import SubmitField


class FormError(FlaskForm):
    submit = SubmitField("Вернуться на главную")
