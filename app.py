import base64

import requests
from flask import Flask, render_template, url_for, redirect, session, request, blueprints

from admin import admin
from data.doctor_model import Reg_Doctor
from cfg import HOST, PORT
from data import db_session
from data.news import News
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.registration import RegistraionForm
from forms.form_error import FormError

app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True, port=PORT, host=HOST)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Reg_User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Reg_User).filter(Reg_User.email == form.email.data).first()

        if user is None:
            return render_template('login.html', message="Такой учетной записи не существует.", form=form)
        if user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("index"))
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    form = RegistraionForm()
    if form.validate_on_submit():
        if form.password.data != form.password_rep.data:
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")

        if form.validate_number_phone(form.number_phone):
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Неверный формат ввода телефона")

        if form.validate_snils(form.snils):
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Неверный формат ввода СНИЛС")

        db_sess = db_session.create_session()
        if db_sess.query(Reg_User).filter(Reg_User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        new_user = Reg_User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.middle_name.data,
            phone_number=form.number_phone.data,
            snils=form.snils.data,
            oms_series=form.series_oms.data,
            oms_number=form.number_oms.data
        )
        new_user.set_hash_psw(form.password.data)

        db_sess.add(new_user)
        db_sess.commit()
        return redirect(url_for('login'))
    return render_template("registration.html", form=form)


@app.route("/profile", methods=['POST', 'GET'])
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user, is_auth=current_user.is_authenticated)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()[-1:-6:-1]
    for i in news:
        i.image = base64.b64encode(i.image).decode("utf-8")

    doctors = requests.get(f'http://{HOST}:{PORT}/admin/doctor_api/doctors', params={'is_active': 'True'}).json()
    return render_template("index.html",
                           title="Главная страница",
                           is_auth=current_user.is_authenticated,
                           news=news,
                           doctors=doctors)


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
