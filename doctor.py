from flask import Flask, render_template, url_for, redirect, flash
from data.doctor_model import Reg_Doctor, Schedule, ScheduleForUser
from cfg import DOCTOR_PORT, DOCTOR_HOST
from data import db_session
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.doctor_login_form import DoctorLoginForm
from forms.form_error import FormError
'''Инициализация всего нужного для app`ы'''
app_doc = Flask('doctor')
login_manager1 = LoginManager()
REMEMBER_COOKIE_SECURE = False
login_manager1.init_app(app_doc)
app_doc.config['SECRET_KEY'] = 'yandexlycerefersdsdasd423423wfsf3345345um_secret_key'


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


'''Аутентификация доктора, автоматом редиректит с главной страницы сюда если доктор не зашел в свой аккаунт'''
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


'''Главная страница докторов'''
@login_required
@app_doc.route("/")
def index():
    info_to_load = {}
    if current_user.is_anonymous:
        return redirect(url_for('login'))
    '''Через контекстный менеджер получаем необходимые данные и потом грузим их в жсон, рендерим шаблон с параметрами'''
    with db_session.create_session() as session:
        all_ticket = session.query(Schedule).filter(Schedule.doc_id == current_user.id).all()
        for info in all_ticket:
            if info.state == 'disable':
                try:
                   info_to_load[info.date.strftime("%d.%m.%Y")].append(
                       {
                           'id': info.id,
                           'time': info.tickets.strftime("%H:%M")
                       }
                   )
                except KeyError:
                    info_to_load[info.date.strftime("%d.%m.%Y")] = [{
                            'id': info.id,
                            'time': info.tickets.strftime("%H:%M")
                        }]
    info_to_load = dict(sorted(info_to_load.items(), key=lambda item: item))

    return render_template('doc_index.html', info=info_to_load, is_auth=current_user.is_authenticated)

@login_required
@app_doc.route('/start_appointment/<int:ticket_id>')
def start_appointment(ticket_id):
    '''рут начала приема, так же получаем данные нужные и рендерим темплейт'''
    with db_session.create_session() as sess:
        user = sess.query(ScheduleForUser).filter(ScheduleForUser.schedule_id == ticket_id).first().user_id
        client_info = sess.query(Reg_User).filter(Reg_User.id == user).first()
        data = {
            'name': client_info.name,
            'patronymic': client_info.patronymic,
            'snils': client_info.snils,
            'oms_number': client_info.oms_number,
            'surname': client_info.surname,
            'email': client_info.email,
            'phone_number': client_info.phone_number,
            'oms_series': client_info.oms_series}

    return render_template('start_appointment.html', user=data, id=ticket_id)


@login_required
@app_doc.route('/end_appointment/<int:ticket_id>')
def end_appointment(ticket_id):
    '''рут заглушка для удаления завершенного посещения'''
    with db_session.create_session() as sess:

        ticket_to_del = sess.query(ScheduleForUser).filter(ScheduleForUser.schedule_id == ticket_id).first()
        global_delete = sess.query(Schedule).filter(Schedule.id == ticket_id).first()
        sess.delete(ticket_to_del)
        sess.delete(global_delete)
        sess.commit()
    flash('Прием завершен')
    return redirect(url_for('index'))


'''далее идут два эрорхендлера, ну тут нечего комментировать'''
@app_doc.errorhandler(401)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        pass
    return render_template("shablon_error.html", form=form, title="Ошбика 401",
                           error_message="У вас нет разрешения на просмотр этого каталога или страницы с использованием предоставленных вами учетных данных.")


@app_doc.errorhandler(404)
def unlogin_user(e):
    form = FormError()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("shablon_error.html", form=form, title="Ошбика 404",
                           error_message="Кажется что-то пошло не так! Страница, которую вы запрашиваете, не существует. Возомжно она устарела, была удалена, или был введён неверный адрес в адресной строке.")


if __name__ == '__main__':
    main()
