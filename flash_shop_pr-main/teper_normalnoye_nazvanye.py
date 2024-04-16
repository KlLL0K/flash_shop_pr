from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user
from data.users import User
from data import db_session
from forms.user import RegisterForm, LoginForm
db_session.global_init("db/blogs.db")
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = '1488'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


products = [
    {
        'name': 'Ноутбук',
        'description': 'Мощный ноутбук с высокой производительностью.',
        'price': 50000,
        'image_url': 'https://example.com/notebook.jpg'
    },
    {
        'name': 'Смартфон',
        'description': 'Современный смартфон с отличной камерой.',
        'price': 25000,
        'image_url': 'https://example.com/smartphone.jpg'
    },
    {
        'name': 'Наушники',
        'description': 'Беспроводные наушники с шумоподавлением.',
        'price': 5000,
        'image_url': 'https://example.com/headphones.jpg'
    }
]


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_session.global_init("db/blogs.db")
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        print(1)
        db_sess = db_session.create_session()
        print(2)
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def index():
    return render_template('index.html', products=products)


@app.route('/base')
def base():
    return render_template('base.html', products=products)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
