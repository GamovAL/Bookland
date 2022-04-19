from flask import Flask, render_template, redirect, request, session, send_from_directory
from flask_login import LoginManager, login_user, current_user
import json

from data import db_session
from data.users import User
from data.book import Book
from forms.login_form import LoginForm
from forms.register import RegisterForm
from data.order import Order, Association
from datetime import datetime, timedelta
from forms.order_form import Order_Form


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():                                     # Авторизация пользователя
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():                                          # Регистрация
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="Этот пользователь уже существует")
        user = User(
            name=form.name.data,
            email=form.email.data,
            telephone=form.telephone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/")
def index():  # главная страница
    q = request.args.get('q')
    # book = db_sess.query.filter(Book.title.contains(q) | Book.description.contains(q)).all()
    if 'basket' not in session:
        session['basket'] = json.dumps({})
    db_sess = db_session.create_session()
    if q:
        book = db_sess.query(Book).filter(Book.title.contains(q) | Book.description.contains(q)).all()
    else:
        book = db_sess.query(Book).all()
    if 'basket' in session:
        basket = json.loads(session['basket'])
    else:
        basket = {}
    return render_template("index.html", books=book, title='Bookland', basket=basket)


@app.route('/add_basket/<int:id>')
def add_basket(id):                             # Функция для корзины добавление книг
    if 'basket' in session:
        basket = json.loads(session['basket'])
        basket[id] = 1
        session['basket'] = json.dumps(basket)
    else:
        session['basket'] = json.dumps({id: 1})
    return redirect('/')


@app.route('/del_basket/<int:id>')
def del_basket(id):                              # Функция для корзины удаление книг
    basket = json.loads(session['basket'])
    basket.pop(str(id))
    session['basket'] = json.dumps(basket)
    return redirect('/')


@app.route('/basket')
def basket():                                   # Корзина
    if 'basket' in session:
        basket = json.loads(session['basket'])
        id_basket = list(map(int, basket.keys()))
        db_sess = db_session.create_session()
        books = db_sess.query(Book).filter(Book.id.in_(id_basket))
        li = []
        for i in books:
            i.count = basket[str(i.id)]
            li.append(i)
        summa = sum(map(lambda x: x.count * x.cost, li))
        order_button = True
        if not basket:
            order_button = False
        return render_template('basket.html', books=books, sum=summa, order_button=order_button)


@app.route('/prepend/<id>')
def prepend(id):
    basket = json.loads(session['basket'])
    basket[id] -= 1
    if basket[id] < 1:
        basket[id] = 1
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/append/<id>')
def append(id):
    basket = json.loads(session['basket'])
    basket[id] += 1
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/del/<id>')
def basket_delet(id):
    basket = json.loads(session['basket'])
    del basket[id]
    session['basket'] = json.dumps(basket)
    return redirect('/basket')


@app.route('/order', methods=['GET', 'POST'])
def order():
    order_form = Order_Form(time_delivery=datetime.now() + timedelta(hours=1))
    if current_user.is_authenticated:
        order_form.user_name.data = current_user.name
        order_form.address.data = current_user.address
        order_form.telephone.data = current_user.telephone
    basket = json.loads(session['basket'])
    if order_form.validate_on_submit():
        db_sess = db_session.create_session()
        order = Order(
            user_name=order_form.user_name.data,
            telephone=order_form.telephone.data,
            address=order_form.address.data,
            time_delivery=order_form.time_delivery.data)
        for book in basket:
            a = Association(count=basket[book])
            a.book = db_sess.query(Book).get(int(book))
            order.books.append(a)
        session['basket'] = json.dumps({})
        db_sess.add(order)
        db_sess.commit()
        return render_template('order_ok.html', title='Заказ принят')
    return render_template('order.html', title='Оформление заказа', form=order_form)


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    # date = datetime.strptime(date, '%Y-%m-%d H:M:f')
    format = '%d.%m.%y, %H:%M'
    return date.strftime(format)


@login_manager.user_loader
def load_user(user_id):  # Авторизация пользователя
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/download_pdf/<id>')
def download_pdf(id):
    db_sess = db_session.create_session()
    pdf = db_sess.query(Book).get(int(id))
    return send_from_directory(path='/static/', directory='static/pdf',
                               filename=pdf.pdf.split('/')[1])


def main():
    db_session.global_init("db/Bookland.sqlite")
    app.run(debug=True)


if __name__ == '__main__':
    main()
