from flask import Flask, render_template, url_for, redirect
from data import db_session
from data.reg_users import Reg_User
from forms.login import LoginForm
from flask_login import LoginManager
from forms.registration import RegistraionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/users.db")
    app.run(debug=True)


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return render_template("base.html")
    return render_template("login.html", form=form)


@app.route("/registration", methods=['POST', 'GET'])
def registration():
    form = RegistraionForm()
    if form.validate_on_submit():
        if form.password.data != form.password_rep.data:
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Reg_User).filter(Reg_User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        new_user = Reg_User(
            email=form.email.data,
            name=form.name.data,
            surname=form.surname.data,
            patronymic=form.middle_name.data,
            pnone_number=form.number_phone.data,
            snils=form.snils.data,
            oms_series=form.series_oms.data,
            oms_number=form.number_oms.data
        )
        new_user.set_hash_psw(form.password.data)

        db_sess.add(new_user)
        db_sess.commit()
        return redirect(url_for('login'))
    return render_template("registration.html", form=form)


@app.route("/")
def index():
    return render_template("index.html", title="Главная страница")


if __name__ == '__main__':
    main()
