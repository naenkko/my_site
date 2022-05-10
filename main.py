import os

from flask import Flask, url_for, request, render_template, redirect, make_response, session

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
        user = db_sess.query(User).filter(User.id == 1).first()
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


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


def main():
    db_session.global_init("db/blogs.db")

    # user = User()
    # user.name = "Nastya"
    # user.surname = "Babenko"
    # user.email = "email@email.ru"
    # user.email = "email@email.ru"
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()

    # news = News(title="Первая новость", content="Привет блог!",
    #             user_id=1, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()
    #
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Вторая новость", content="Уже вторая запись!",
    #             user=user, is_private=False)
    # db_sess.add(news)
    # db_sess.commit()
    #
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Личная запись", content="Эта запись личная",
    #             is_private=True)
    # user.news.append(news)
    # db_sess.commit()

    # вывести первого юзера
    # user = db_sess.query(User).first()
    # print(user.name)

    # печать всех значений юзер
    # for user in db_sess.query(User).all():
    #     print(user)

    # применить фильтр и вывести нужное
    # for user in db_sess.query(User).filter((User.id > 1) | (User.email.notilike("%1%"))):
    #     print(user)

    # изменить данные
    # user = db_sess.query(User).filter(User.id == 1).first()
    # print(user)
    # user.name = "Измененное имя пользователя"
    # db_sess.commit()

    # удалить какие-то данные
    # db_sess.query(User).filter(User.id >= 2).delete()
    # db_sess.commit()

    # удалить выбранную запись
    # user = db_sess.query(User).filter(User.id == 2).first()
    # db_sess.delete(user)
    # db_sess.commit()

    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()