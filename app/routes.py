from flask import render_template, url_for
from app import app, db, moment
from app.models import Group, Test


@app.route('/')
@app.route('/index')
def index():
    groups = Group.query.all()

    return render_template( "index.html", title = "Все тесты", menu = "Меню", groups = groups )


@app.route('/test/<int:id>')
def test(id):
    test = Test.query.get(id)

    return render_template( "test-base.html", title = f"Тесты / {test.name}", menu = "Вопросы", test = test )


@app.route('/add')
def add():
    return 'ok'
