from flask import Flask, request, render_template, redirect

from PIL import Image

from data import db_session
from forms.user import RegisterForm
from loginform import LoginForm
from data.users import User
from data.news import News

from flask_login import LoginManager, login_user, current_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
        return render_template("profile.html", title='Профиль пользователя')
    elif request.method == 'POST':
        f = request.files['file']
        img = Image.open(f)
        way = 'static/img/' + 'img_' + current_user.username + '.jpg'
        img.save(way)

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        print(user.photo)
        user.photo = way
        db_sess.commit()

        return render_template("profile.html", title='Профиль пользователя')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.username == form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main_page")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/main_page')
def main_page():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@app.route('/register', methods=['GET', 'POST'])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Почта используется другим пользователем")
        if db_sess.query(User).filter(User.username == form.username.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Имя пользователя занято")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            username=form.username.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        user.photo = 'static/img/no_image_profile.jpeg'
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    db_session.global_init("db/blogs.db")

    news = News(title="Первая новость", content="Привет блог!",
                user_id=1, is_private=False)
    db_sess = db_session.create_session()
    db_sess.add(news)
    db_sess.commit()

    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()