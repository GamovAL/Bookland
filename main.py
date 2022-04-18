from flask import Flask, render_template, request, session, send_from_directory
from flask_login import LoginManager
import json

from data import db_session
from data.users import User
from data.book import Book


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():       #главная страница
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


@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    # date = datetime.strptime(date, '%Y-%m-%d H:M:f')
    format = '%d.%m.%y, %H:%M'
    return date.strftime(format)


@login_manager.user_loader
def load_user(user_id):                      # Авторизация пользователя
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
