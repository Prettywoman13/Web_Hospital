from flask_wtf import FlaskForm
from wtforms import IntegerField, TimeField, SubmitField
from wtforms.validators import DataRequired



class DoctorScheduleForm(FlaskForm):
    worktime_from = TimeField('Прием с  ', validators=[DataRequired()])
    worktime_until = TimeField('Прием до  ', validators=[DataRequired()])
    lunch_from = TimeField('Обед с ', validators=[DataRequired()])
    lunch_until = TimeField('Обед до',validators=[DataRequired()])
    timedelta = IntegerField('Время на один приём(в мин)  ', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
