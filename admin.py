import base64
from flask import render_template, url_for, redirect, session, request, jsonify, flash
from requests import post, get, put, patch, delete
from forms.edit_doc_on_page import Change_Btns
from data.doctor_model import Reg_Doctor
from cfg import HOST, admin_id, PORT
from data.news import News
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from flask_login import login_required, current_user
from forms.edit_doctor_validator import ChangeDoctorForm
from forms.news_form import NewsForm
from forms.reg_doctor import RegistraionDoctorForm
from flask import Blueprint
admin = Blueprint('admin', __name__, template_folder='templates')
admin_api = Api(admin)
doc_states = {
    'True': True,
    'False': False
}
doctor_api_parser = reqparse.RequestParser()
doctor_api_parser.add_argument('login')
doctor_api_parser.add_argument('password')
doctor_api_parser.add_argument('name')
doctor_api_parser.add_argument('middle_name')
doctor_api_parser.add_argument('surname')
doctor_api_parser.add_argument('prof')
doctor_api_parser.add_argument('img')
doctor_api_parser.add_argument('is_active')


@login_required
@admin.route("/", methods=['GET', 'POST'])
def admin_index_page():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            abort(401)
        if request.method == 'POST':
            if "add_news" in request.form:
                return redirect(url_for('admin.create_news_page'))
            elif "get_all_doc" in request.form:
                return redirect(url_for('admin.show_doctors'))

        return render_template('admin_index.html', is_auth=current_user.is_authenticated,)
    abort(401)


@login_required
@admin.route("/add_news", methods=['GET', 'POST'])
def create_news_page():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            abort(401)
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

    return abort(401)


@login_required
@admin.route('/list_doctors', methods=['GET', 'POST'])
def show_doctors():
    doctors = get(f'http://{HOST}:{PORT}/admin/doctor_api/doctors').json()['doctors']
    form = Change_Btns()
    return render_template('show_doctors.html', is_auth=current_user.is_authenticated,
                           doctors=doctors, form=form)


@admin.route('/delete_doctor/<int:doc_id>', methods=['GET'])
def del_doctor(doc_id):
    delete(f'http://{HOST}:{PORT}/admin/doctor_api/{doc_id}')
    flash('Доктор удален')
    return redirect(url_for('admin.admin_index_page'))


@login_required
@admin.route('/add_doctor', methods=['GET', 'POST'])
def create_doctor():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            abort(401)
        form = RegistraionDoctorForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('admin_reg_doctor.html',
                                       form=form,
                                       is_auth=current_user.is_authenticated,
                                       message='пароли доктора не совпадают')
            img = base64.b64encode(request.files["img1"].stream.read())
            post(f'http://{HOST}:{PORT}/admin/doctor_api/1',
                 json={
                     'login': form.login.data,
                     'password': form.password.data,
                     'name': form.name.data,
                     'middle_name': form.middle_name.data,
                     'surname': form.surname.data,
                     'prof': form.prof.data,
                     'img': str(img),
                     'is_active': bool(form.is_active.data)
                 })
            flash('Доктор создан')
            return redirect(url_for('admin.admin_index_page'))

        return render_template('admin_reg_doctor.html', form=form, is_auth=current_user.is_authenticated)

    abort(401)


@login_required
@admin.route('/update_doctor/<int:doc_id>', methods=['GET', 'POST'])
def change_doctor_data(doc_id):
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            abort(401)
        else:
            doc_data = get(f'http://{HOST}:{PORT}/admin/doctor_api/{doc_id}')
            if doc_data.status_code != 200:
                abort(doc_data.status_code)
            doc_data = doc_data.json()['doctor']
            form = ChangeDoctorForm(
                name=doc_data['name'],
                surname=doc_data['surname'],
                middle_name=doc_data['middle_name'],
                prof=doc_data['prof'],
                is_active=doc_data['is_active'])
            if form.validate_on_submit():

                img = base64.b64encode(request.files["img1"].stream.read())
                if len(img) == 0:
                    patch(f'http://{HOST}:{PORT}/admin/doctor_api/{doc_id}',
                          json={
                              'name': form.name.data,
                              'middle_name': form.middle_name.data,
                              'surname': form.surname.data,
                              'prof': form.prof.data,
                              'is_active': str(form.is_active.data)
                          })
                else:
                    patch(f'http://{HOST}:{PORT}/admin/doctor_api/{doc_id}',
                        json={
                            'name': form.name.data,
                            'middle_name': form.middle_name.data,
                            'surname': form.surname.data,
                            'prof': form.prof.data,
                            'img': str(img)
                        })
                flash('Данные изменены')
                return redirect(url_for('admin.admin_index_page'))
            return render_template('change_doctor.html', form=form, is_auth=current_user.is_authenticated)
    else:
        abort(401)


class Doctor(Resource):
    def get(self, doctor_id):
        db_sess = db_session.create_session()
        doc = db_sess.query(Reg_Doctor).filter(Reg_Doctor.id == doctor_id).first()
        if not doc:
            abort(404, message=f"Doctor with id:{doctor_id} not found")
        return jsonify(
            {'doctor': {
                'login': doc.login,
                'name': doc.name,
                'middle_name': doc.middle_name,
                'surname': doc.surname,
                'prof': doc.prof,
                'is_active': doc.is_active
            }})

    def post(self, doctor_id):
        all_args = doctor_api_parser.parse_args()
        db_sess = db_session.create_session()
        img = bytes(all_args['img'], encoding='utf-8')[2:-1]
        new_doctor = Reg_Doctor(
            login=all_args['login'],
            name=all_args['name'],
            middle_name=all_args['middle_name'],
            surname=all_args['surname'],
            prof=all_args['prof'],
            image=img,
            is_active=doc_states[all_args['is_active']]
        )

        new_doctor.set_hash_psw(all_args['password'])
        db_sess.add(new_doctor)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def patch(self, doctor_id):
        all_args = doctor_api_parser.parse_args()
        db_sess = db_session.create_session()
        doctor_data = db_sess.query(Reg_Doctor).filter(Reg_Doctor.id == doctor_id).first()
        doctor_data.name = all_args['name']
        doctor_data.surname = all_args['surname']
        doctor_data.middle_name = all_args['middle_name']
        doctor_data.prof = all_args['prof']
        if all_args['img']:
            img = bytes(all_args['img'], encoding='utf-8')[2:-1]
            doctor_data.image = img
        doctor_data.is_active = doc_states[all_args['is_active']]
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
            only=('login','id', 'name', 'middle_name', 'surname', 'prof', 'image', 'is_active')) for item in doc]})


admin_api.add_resource(ListDoctors, '/doctor_api/doctors')
admin_api.add_resource(Doctor, '/doctor_api/<doctor_id>')
