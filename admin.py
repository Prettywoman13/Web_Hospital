from flask import Flask, render_template, url_for, redirect, session, request, jsonify
from cfg import HOST, admin_id
from data.news import News
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
from data.reg_users import Reg_User
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.login import LoginForm
from forms.news_form import NewsForm
from forms.registration import RegistraionForm
from flask import Blueprint
admin = Blueprint('admin_api', __name__, template_folder='templates')
admin_api = Api(admin)

@login_required
@admin.route("/create_news", methods=['GET', 'POST'])
def create_news_page():
    if current_user.is_authenticated:
        if session['_user_id'] != admin_id:
            return '''
            ошибка доступа, обратитесь к системному администратору
            '''
        else:
            print(session['_user_id'])
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


class Patient(Resource):

    def get(self, id):
        # abort_if_news_not_found(news_id)
        session = db_session.create_session()
        user = session.query(Reg_User).get(id)
        print(user.__dict__)
        return jsonify({'user': user.to_dict(
            only=('id', 'pnone_number'))})


admin_api.add_resource(Patient, '/<id>')
