from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, EmailField, StringField, IntegerField, TelField
from wtforms.validators import DataRequired, ValidationError


class RegistraionForm(FlaskForm):
    def validate_snils(form, field):
        try:
            number = str(field.data)

            if not number.isdigit():
                raise ValidationError

            if len(number) != 11:
                raise ValidationError

        except ValidationError:
            return True
        return False

    def validate_number_phone(form, field):
        msg_value = "Неверный формат"
        try:
            number = field.data.replace(" ", "").replace("\t", "")
            if not (number[0] == "8" or number[:2] == "+7"):
                raise ValidationError

            if not (number.count("(") == number.count(")") <= 1 and
                    number.find("(") <= number.find(")")):
                raise ValidationError

            if number.count("--"):
                raise ValidationError

            if number[0] == "-" or number[-1] == "-":
                raise ValidationError

            number = number.replace("-", "").replace("(", "").replace(")", "")

            if not (number[1:].isdigit()):
                raise ValidationError

            if number[0] == "8":
                number = "+7" + number[1:]

            if not (len(number) == 12):
                raise ValidationError

        except ValidationError:
            return True
        return False

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_rep = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    snils = IntegerField('СНИЛС', validators=[DataRequired()])
    number_phone = TelField('Номер телефона', validators=[DataRequired(), validate_number_phone])
    series_oms = IntegerField('Серия полиса ОМС (необязательно)'    )
    number_oms = IntegerField('Номер полиса ОМС', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')