import base64
import datetime

import requests
from flask import Flask, render_template, url_for, redirect, session, request, blueprints, flash
from admin import admin
from data.doctor_model import Reg_Doctor, Schedule, ScheduleForUser
from cfg import HOST, PORT, admin_id
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
    schedule_info = {}
    print('123')
    # некрасаивый кусок кода, сюда лучше не смотреть )
    with db_session.create_session() as sess:
        user_tickets = sess.query(ScheduleForUser).filter(ScheduleForUser.user_id == user.id).all()
        user_tickets = [x.schedule_id for x in user_tickets]
        all_tickets = sess.query(Schedule).all()
        for tickt_num, i in enumerate(all_tickets):
            if i.id in user_tickets and i.date >= datetime.datetime.today().date():
                doc = sess.query(Reg_Doctor).filter(Reg_Doctor.id == i.doc_id).first()
                schedule_info[tickt_num] = {
                    'date': i.date,
                    'time': i.tickets,
                    'doc_fio': f"{doc.surname} {doc.name} {doc.middle_name}",
                    'doc_prof': doc.prof
                }
    print(schedule_info)
    return render_template('profile.html', user=user, is_auth=current_user.is_authenticated,
                           is_admin=session['_user_id'] == admin_id, info=schedule_info)


@app.route("/")
def index():
    print(current_user)
    session['url'] = url_for('index')
    db_sess = db_session.create_session()
    news = db_sess.query(News).all()[-1:-6:-1]
    for i in news:
        i.image = base64.b64encode(i.image).decode("utf-8")

    try:
        is_admin = session['_user_id'] == admin_id
    except KeyError:
        is_admin = False

    doctors = requests.get(f'http://{HOST}:{PORT}/admin/doctor_api/doctors', params={'is_active': 'True'}).json()

    return render_template("index.html",
                           title="Главная страница",
                           is_auth=current_user.is_authenticated,
                           news=news,
                           doctors=doctors,
                           is_admin=is_admin)


@app.route('/appointment')
def make_an_appointment():
    profs = []
    db_sess = db_session.create_session()
    doctors_query = db_sess.query(Reg_Doctor).filter(Reg_Doctor.is_active == True).all()
    for i in doctors_query:
        if i.prof not in profs:
            profs.append(i.prof)
    profs = sorted(profs)

    try:
        is_admin = session['_user_id'] == admin_id
    except KeyError:
        is_admin = False
    return render_template("appointment_list.html",
                           title="Запись к врачу",
                           is_auth=current_user.is_authenticated,
                           is_admin=is_admin, profs=profs)


@app.route('/doc_with_prof/<doc_prof>')
def doc_with_prof(doc_prof):
    doctors = requests.get(f'http://{HOST}:{PORT}/admin/doctor_api/doctors', params={'prof': doc_prof}).json()['doctors']
    return render_template('doc_by_prof.html', is_auth=current_user.is_authenticated, doctors=doctors)


@app.route('/get_ticket/<int:doc_id>', methods=['POST', 'GET'])
def get_ticket(doc_id):
    sess = db_session.create_session()
    tickets = sess.query(Schedule).filter(Schedule.doc_id == doc_id, Schedule.state == 'active').all()
    info_for_user = {}
    for i in tickets:
        try:

            info_for_user[i.date.strftime("%D")].append(
                {'time': i.tickets.strftime("%H:%M"), 'id': i.id})

        except KeyError:
            info_for_user[i.date.strftime("%D")] = []
            info_for_user[i.date.strftime("%D")].append(
                {'time': i.tickets.strftime("%H:%M"), 'id': i.id})
    return render_template('get_ticket.html', is_auth=current_user.is_authenticated, tickets=info_for_user)


@app.route('/get_ticket_submit/<int:ticket_id>')
def get_ticket_submit(ticket_id):
    print('123')
    sess = db_session.create_session()
    selected_ticket = ScheduleForUser(
        schedule_id=ticket_id,
        user_id=current_user.id
    )

    sess.add(selected_ticket)
    ticket_to_change = sess.query(Schedule).filter(Schedule.id == ticket_id).first()
    print(ticket_to_change)
    ticket_to_change.state = 'disable'
    sess.commit()
    ticket_to_change = sess.query(Schedule).filter(Schedule.id == ticket_id).first()
    print(ticket_to_change.state)
    flash('Вы записаны')
    return redirect(url_for('profile'))


@app.errorhandler(401)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("shablon_error.html",
                           form=form, title="Ошбика 401",
                           error_message="У вас нет разрешения на просмотр этого каталога или страницы с "
                                         "использованием предоставленных вами учетных данных.")


@app.errorhandler(404)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("shablon_error.html", form=form, title="Ошбика 404",
                           error_message="Кажется что-то пошло не так! Страница, которую вы ищите, не существует."
                                         "Возмoжно она устарела, была удалена, "
                                         "или был введён неверный адрес в адресной строке.")


if __name__ == '__main__':
    main()
