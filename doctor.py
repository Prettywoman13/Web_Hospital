from flask_login import current_user, login_user, LoginManager
from flask import redirect, url_for, render_template
from cfg import HOST, PORT
from data import db_session
from data.doctor_model import Reg_Doctor
from flask_restful import reqparse, abort, Api, Resource
from forms.doctor_login_form import  DoctorLoginForm
from flask import Blueprint
doctor = Blueprint('doctor', __name__, template_folder='templates')
login_manager = LoginManager()
admin_api = Api(doctor)


@doctor.route('/', methods=['GET', 'POST'])
def main():
    return current_user


@doctor.route('/login', methods=['GET', 'POST'])
def login():
    form = DoctorLoginForm()
    if not current_user.is_authenticated:

        if form.validate_on_submit():

            db_sess = db_session.create_session()
            user = db_sess.query(Reg_Doctor).filter(Reg_Doctor.login == form.login.data).first()

            if user is None:
                return render_template('login_doc.html', message="Такой учетной записи не существует.", form=form)
            if user.check_password(form.password.data):

                login_user(user)
                return redirect(url_for('doctor.main'))
            return render_template('login_doc.html', message="Неправильный логин или пароль", form=form)
    return render_template('login_doc.html', title='Авторизация', form=form)
