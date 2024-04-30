import os
import sqlite3
from flask import Flask, render_template, redirect, request, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user
from telegram.ext import CommandHandler
from telegram.ext import Application, MessageHandler, filters
from config import BOT_TOKEN
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


def create_product_database():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price REAL,
            description TEXT,
            image_url TEXT
        )
    ''')
    conn.commit()
    conn.close()


def get_products_from_database():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, description, price FROM Products')
    products = []
    for row in cursor.fetchall():
        name, description, price = row
        product = {
            'name': name,
            'description': description,
            'price': price,
            'image_url': ''  # Добавьте URL-адрес изображения, если он хранится в базе данных
        }
        products.append(product)
    conn.close()
    return products


products = get_products_from_database()


def add_product_to_database(name, price, description, image_url):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
                INSERT INTO Products (name, price, description, image_url) VALUES (?, ?, ?, ?)
            ''', (name, price, description, image_url))
    conn.commit()
    conn.close()


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']

        # Получение файла изображения из запроса
        image_file = request.files['image']
        if image_file:
            # Сохранение файла в папке static/img
            upload_folder = os.path.join(app.root_path, 'static', 'img')
            image_path = os.path.join(upload_folder, image_file.filename)
            image_file.save(image_path)
        else:
            image_path = None

        add_product_to_database(name, price, description, image_path)
        return redirect(url_for('index'))
    else:
        return render_template('add_prod.html')


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
    global products
    products = get_products_from_database()
    return render_template('base.html', products=products)


cart = []


@app.route('/cart')
def view_cart():
    total_price = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total_price=total_price)


print(products)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    if request.method == 'POST':
        product_index = int(request.form['product_index'])  # Получаем индекс выбранного продукта
        if 0 <= product_index < len(products):
            product = products[product_index]  # Получаем выбранный продукт из списка
            cart.append(product)
            print("Товар добавлен в корзину:", product)
            print("Содержимое корзины:", cart)
            return render_template('base.html', products=products)
        else:
            return "Продукт с указанным индексом не найден!"


order_info = {}


@app.route('/checkout')
def checkout():
    return render_template('checkout.html')


@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if request.method == 'POST':
        # Получаем данные из формы
        card_number = request.form['card_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        city = request.form['city']

        # Сохраняем информацию о заказе
        order_info['card_number'] = card_number
        order_info['first_name'] = first_name
        order_info['last_name'] = last_name
        order_info['city'] = city
        print(order_info)
        return "Заказ успешно подтвержден!"


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    create_product_database()
    app.run(port=8080, host='127.0.0.1')

