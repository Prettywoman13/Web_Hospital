from flask_wtf import FlaskForm
from wtforms import TimeField, SubmitField


class GetTicketForm(FlaskForm):
   get_ticket = SubmitField('Найти талоны')