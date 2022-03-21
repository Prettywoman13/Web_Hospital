from flask import Flask, render_template

from forms.login import LoginForm
from forms.registration import RegistraionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.run()


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("HTML/login.html", form=form)


@app.route("/registration")
def registration():
    form = RegistraionForm()
    return render_template("HTML/registration.html", form=form)


if __name__ == '__main__':
    main()
