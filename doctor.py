import base64

import requests
from flask import Flask, render_template, url_for, redirect, session, request, blueprints
from forms.doctor_login_form import DoctorLoginForm
from data.doctor_model import Reg_Doctor
from cfg import HOST, DOCTOR_PORT
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.form_error import FormError

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'ysdf2342k3j4kl234jandexlyceum_secret_key'


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True, port=DOCTOR_PORT, host=HOST)


@login_manager.user_loader
def load_user(doc_id):
    db_sess = db_session.create_session()
    return db_sess.query(Reg_Doctor).get(doc_id)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
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
            login_user(user, remember=True)
            print(current_user)
            return redirect(url_for("index"))
        return render_template('login_doc.html', message="Неправильный логин или пароль", form=form)
    return render_template('login_doc.html', title='Авторизация', form=form)


# @app.route("/profile", methods=['POST', 'GET'])
# @login_required
# def profile():
#     user = current_user
#     return render_template('profile.html', user=user, is_auth=current_user.is_authenticated)


@app.route("/")
def index():
    print(current_user)
    return f'приветствую, вас, доктор! {current_user}'


@app.errorhandler(401)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        pass
    return render_template("shablon_error.html", form=form, title="Ошбика 401", error_message=
    "У вас нет разрешения на просмотр этого каталога или страницы с использованием предоставленных вами учетных данных.")


@app.errorhandler(404)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("shablon_error.html", form=form, title="Ошбика 404", error_message="Кажется что-то пошло не так! Страница, которую вы запрашиваете, не существует. Возомжно она устарела, была удалена, или был введён неверный адрес в адресной строке.")


if __name__ == '__main__':
    main()
