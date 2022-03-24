from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField, FileField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    description = TextAreaField('Новость', validators=[DataRequired()])
    img_picker = FileField('Изображение (Необязательно)')
    submit = SubmitField('Опубликовать')
