from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from requests import post
from data.doctor_model import Reg_Doctor
from cfg import HOST, admin_id, PORT
from data.news import News
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.news_form import NewsForm
from forms.reg_doctor import RegistraionDoctorForm
from flask import Blueprint
admin = Blueprint('admin', __name__, template_folder='templates')
admin_api = Api(admin)
doctor_api_parser = reqparse.RequestParser()
doctor_api_parser.add_argument('login', required=True)
doctor_api_parser.add_argument('password', required=True)
doctor_api_parser.add_argument('name', required=True)
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
                if form.password.data != form.password_again.data:
                    return render_template('admin_reg_doctor.html',
                                           form=form,
                                           is_auth=current_user.is_authenticated,
                                           message='пароли не совпадают')

                post(f'http://{HOST}:{PORT}/admin/doctor_api/1',
                     json={
                         'login': form.login.data,
                         'password': form.password.data,
                         'name': form.name.data,
                         'middle_name': form.middle_name.data,
                         'surname': form.surname.data,
                         'prof': form.prof.data})

            return render_template('admin_reg_doctor.html', form=form, is_auth=current_user.is_authenticated)


class Patient(Resource):

    def get(self, id):
        session = db_session.create_session()
        user = session.query(Reg_User).get(id)
        print(user.__dict__)
        return jsonify({'user': user.to_dict(
            only=('id', 'pnone_number'))})


class Doctor(Resource):
    def get(self, doctor_id):
        db_sess = db_session.create_session()
        doc = db_sess.query(Reg_Doctor).filter(Reg_Doctor.id == doctor_id).first()
        if not doc:
            abort(404, message=f"Doctor with id:{doctor_id} not found")
        return jsonify(
            {'doctor': {
                'name': doc.login,
                'middle_name': doc.middle_name,
                'surname': doc.surname,
                'prof': doc.prof
                }
            })

    def post(self, doctor_id):
        all_args = doctor_api_parser.parse_args()
        db_sess = db_session.create_session()
        new_doctor = Reg_Doctor(
            login=all_args['login'],
            name=all_args['name'],
            middle_name=all_args['middle_name'],
            surname = all_args['surname'],
            prof = all_args['prof'])
        new_doctor.set_hash_psw(all_args['password'])
        db_sess.add(new_doctor)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def delete(self, doctor_id):
        db_sess = db_session.create_session()
        doctor_to_delete = db_sess.query(Reg_Doctor).filter(Reg_Doctor.id == doctor_id).first()
        db_sess.delete(doctor_to_delete)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ListDoctors(Resource):
    def get(self):
        db_sess = db_session.create_session()
        doc = db_sess.query(Reg_Doctor).all()
        return jsonify({'doctors': [item.to_dict(
            only=('id', 'name', 'middle_name', 'surname', 'prof')) for item in doc]})



admin_api.add_resource(ListDoctors, '/doctor_api/doctors')
admin_api.add_resource(Doctor, '/doctor_api/<doctor_id>')
