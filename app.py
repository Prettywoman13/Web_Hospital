import base64
import datetime
import os

import requests
from flask import Flask, render_template, url_for, redirect, session, request, blueprints, flash
from sqlalchemy.orm.exc import UnmappedInstanceError

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
'''Инициализация приложения '''
app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/users.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)



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
    ''' Рут входа в аккаунт для пользователя, не знаю, кто тут комментировать вроде все ясно'''
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
    '''Рут регистрации пользователя, ничего не скажу, сначала валидируем данные, потом в бд пихаем'''
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
    schedule_info = []
    # некрасаивый кусок кода, сюда лучше не смотреть ), получаем тут данные для пользователя, потом сортируем и закидываем в шаблон
    with db_session.create_session() as sess:
        user_tickets = sess.query(ScheduleForUser).filter(ScheduleForUser.user_id == user.id).all()
        user_tickets = [x.schedule_id for x in user_tickets]
        all_tickets = sess.query(Schedule).all()
        for tickt_num, i in enumerate(all_tickets):
            if i.id in user_tickets and i.date >= datetime.datetime.today().date():
                doc = sess.query(Reg_Doctor).filter(Reg_Doctor.id == i.doc_id).first()
                schedule_info.append({
                    'id': i.id,
                    'date': i.date,
                    'time': i.tickets,
                    'doc_fio': f"{doc.surname} {doc.name} {doc.middle_name}",
                    'doc_prof': doc.prof
                })
    # сортировка талонов по дате и времени
    schedule_info = sorted(schedule_info, key=lambda x: (x['date'], x['time']))

    return render_template('profile.html', user=user, is_auth=current_user.is_authenticated, is_admin=session['_user_id'] == admin_id, info=schedule_info)


@app.route("/")
def index():
    '''Главная страница сайта, ничего нового, берем из бд первые 5 новостей и рендерим шаблон с данными'''
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


@app.route('/appointment', methods=['POST', 'GET'])
@login_required
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
@login_required
def doc_with_prof(doc_prof):
    '''Получаем всех докторов по профессии'''
    doctors = requests.get(f'http://{HOST}:{PORT}/admin/doctor_api/doctors', params={'prof': doc_prof}).json()['doctors']
    return render_template('doc_by_prof.html', is_auth=current_user.is_authenticated, doctors=doctors)


@app.route('/get_ticket/<int:doc_id>', methods=['POST', 'GET'])
@login_required
def get_ticket(doc_id):
    '''Рут для получения всех талонов на все даты по id доктора, парсим из бд и передаем в шаблон'''
    sess = db_session.create_session()
    tickets = sess.query(Schedule).filter(Schedule.doc_id == doc_id, Schedule.state == 'active', Schedule.date >= datetime.datetime.today().date()).all()
    info_for_user = {}
    for i in tickets:
        try:

            info_for_user[i.date.strftime("%d.%m.%Y")].append(
                {'time': i.tickets.strftime("%H:%M"), 'id': i.id})

        except KeyError:
            info_for_user[i.date.strftime("%d.%m.%Y")] = []
            info_for_user[i.date.strftime("%d.%m.%Y")].append(
                {'time': i.tickets.strftime("%H:%M"), 'id': i.id})

    return render_template('get_ticket.html', is_auth=current_user.is_authenticated,
                           tickets=dict(sorted(info_for_user.items(), key=lambda item: item)))


'''Рут для завершения взятия талона, грубо говоря затычка в которй просто делаем пару запросов и редиректим в профиль'''
@app.route('/get_ticket_submit/<int:ticket_id>', methods=['POST', 'GET'])
@login_required
def get_ticket_submit(ticket_id):
    sess = db_session.create_session()
    selected_ticket = ScheduleForUser(
        schedule_id=ticket_id,
        user_id=current_user.id
    )

    sess.add(selected_ticket)
    ticket_to_change = sess.query(Schedule).filter(Schedule.id == ticket_id).first()
    ticket_to_change.state = 'disable'
    sess.commit()
    flash('Вы записаны')
    return redirect(url_for('profile'))


@app.route('/cancel_ticket/<int:ticket_id>')
@login_required
def cancel_ticket(ticket_id):
    '''Отмена талона, делает пару запросов в бд и потом редиректит назад'''
    with db_session.create_session() as sess:
        try:
            query = sess.query(Schedule).filter(Schedule.id == ticket_id).first()
            query.state = 'active'
            query2 = sess.query(ScheduleForUser).filter(ScheduleForUser.schedule_id == ticket_id).first()
            sess.delete(query2)
            sess.commit()
        except UnmappedInstanceError:
            pass

    flash('Талон отменён')
    return redirect(url_for('profile'))



@app.route('/del_news/<int:news_id>')
@login_required
def del_news(news_id):
    '''Удаление новости по ее id'''
    with db_session.create_session() as sess:
        ntd = sess.query(News).filter(News.id == news_id).first()
        sess.delete(ntd)
        sess.commit()
    return redirect(url_for('index'))


'''эрорхендлеры, не знаю что сказать:)'''


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



main()
