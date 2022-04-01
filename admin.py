from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from requests import post

from cfg import HOST, admin_id, PORT
from data.news import News
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.news_form import NewsForm
from forms.reg_doctor import RegistraionDoctorForm
from flask import Blueprint
admin = Blueprint('admin_api', __name__, template_folder='templates')
admin_api = Api(admin)
doctor_api_parser = reqparse.RequestParser()
doctor_api_parser.add_argument('login', required=True)
doctor_api_parser.add_argument('password', required=True)
doctor_api_parser.add_argument('first_name', required=True)
doctor_api_parser.add_argument('middle_name', required=True)
doctor_api_parser.add_argument('surname', required=True)
doctor_api_parser.add_argument('prof', required=True)


@login_required
@admin.route("/create_news", methods=['GET', 'POST'])
def create_news_page():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            return '''
            ошибка доступа, обратитесь к системному администратору
            '''
        else:

            form = NewsForm()

            if form.validate_on_submit():
                db_sess = db_session.create_session()

                new_news = News()

                new_news.title = form.title.data
                new_news.description = form.description.data
                new_news.image = request.files["img1"].stream.read()

                db_sess.add(new_news)
                db_sess.commit()
                return redirect(url_for('index'))

            return render_template("create_news.html",
                                   title="Создать новость",
                                   is_auth=current_user.is_authenticated,
                                   form=form)

    return '''
    вы не зареганы
    '''


@login_required
@admin.route('/add_doctor', methods=['GET', 'POST'])
def create_doctor():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            return '''
            ошибка доступа, обратитесь к системному администратору
            '''
        else:
            form = RegistraionDoctorForm()
            if form.validate_on_submit():
                post(f'http://{HOST}:{PORT}/admin/create_doctor_api',
                     json={
                         'login': form.login.data,
                         'password': form.password.data,
                         'first_name': form.name.data,
                         'middle_name': form.middle_name.data,
                         'surname': form.surname.data,
                         'prof': form.prof.data})
            return render_template('admin_reg_doctor.html', form=form)



class Patient(Resource):

    def get(self, id):
        # abort_if_news_not_found(news_id)
        session = db_session.create_session()
        user = session.query(Reg_User).get(id)
        print(user.__dict__)
        return jsonify({'user': user.to_dict(
            only=('id', 'pnone_number'))})


class Doctor(Resource):
    def get(self, id):
        pass

    def post(self):
        all_args = doctor_api_parser.parse_args()
        print(all_args)


admin_api.add_resource(Doctor, '/create_doctor_api')
admin_api.add_resource(Patient, '/<id>')
# post(
#                 f'http://127.0.0.1:8020/admin/create_doctor',
#                 json={
#                     'doctor_id': 1,
#                     'first_name': 'Андрей',
#                     'second_name': 'Дмитриевич',
#                     'last_name': 'Свечников',
#                     'prof': 'Проктолог'
#                 }
#             )