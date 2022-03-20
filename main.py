from flask import Flask, render_template

from forms.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    app.run()


@app.route("/login")
def login():
    form = LoginForm()
    return render_template("HTML/login.html", form=form)


if __name__ == '__main__':
    main()
