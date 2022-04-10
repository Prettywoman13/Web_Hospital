import base64

import requests
from flask import Flask, render_template, url_for, redirect, session, request, blueprints

from admin import admin
from data.doctor_model import Reg_Doctor
from cfg import HOST, DOCTOR_PORT, DOCTOR_HOST
from data import db_session
from data.news import News
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.doctor_login_form import DoctorLoginForm
from forms.login import LoginForm
from forms.registration import RegistraionForm
from forms.form_error import FormError

app_doc = Flask('doctor')
login_manager1 = LoginManager()
REMEMBER_COOKIE_SECURE = False
login_manager1.init_app(app_doc)
app_doc.config['SECRET_KEY'] = 'yandexlycereferf3345345um_secret_key'


def main():
    db_session.global_init("db/users.db")
    app_doc.run(debug=True, port=DOCTOR_PORT, host=DOCTOR_HOST)


@login_manager1.user_loader
def load_user(id):
    db_sess = db_session.create_session()
    return db_sess.query(Reg_Doctor).get(id)


@app_doc.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app_doc.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = DoctorLoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Reg_Doctor).filter(Reg_Doctor.login == form.login.data).first()

        if user is None:
            return render_template('login_doc.html', message="Такой учетной записи не существует.", form=form)
        if user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        return render_template('login_doc.html', message="Неправильный логин или пароль", form=form)
    return render_template('login_doc.html', title='Авторизация', form=form)


# @app.route("/profile", methods=['POST', 'GET'])
# @login_required
# def profile():
#     user = current_user
#     return render_template('profile.html', user=user, is_auth=current_user.is_authenticated)


@app_doc.route("/")
def index():
    return f'Привет доктор {current_user.login}'

@app_doc.errorhandler(401)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        pass
    return render_template("shablon_error.html", form=form, title="Ошбика 401", error_message=
    "У вас нет разрешения на просмотр этого каталога или страницы с использованием предоставленных вами учетных данных.")


@app_doc.errorhandler(404)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("shablon_error.html", form=form, title="Ошбика 404", error_message="Кажется что-то пошло не так! Страница, которую вы запрашиваете, не существует. Возомжно она устарела, была удалена, или был введён неверный адрес в адресной строке.")


if __name__ == '__main__':
    main()
