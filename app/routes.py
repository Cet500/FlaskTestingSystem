from flask import render_template, url_for
from app import app, db, moment
from app.models import Group, Test


@app.route('/')
@app.route('/index')
def index():
    groups = Group.query.all()

    return render_template( "index.html", title = "Все тесты", menu = "Тесты по группам", groups = groups )


@app.route('/group/<int:id>')
def group(id):
    group = Group.query.get(id)

    link = url_for( 'index' )
    path = f"<a href='{link}'>Все тесты</a> / {group.title}"

    return  render_template( "group.html", title = f"{group.title}", path = path, menu = "Тесты в группе", group = group )


@app.route('/test/<int:id>')
def test(id):
    test  = Test.query.get(id)
    group = Group.query.get(test.id_group)

    link0 = url_for( 'index' )
    link1 = url_for( 'group', id = group.id )
    path  = f"<a href={link0}>Все тесты</a> / <a href={link1}>{group.title}</a> / {test.name}"

    return render_template( "test-base.html", title = f"{test.name}", path = path, test = test )


@app.route('/add')
def add():
    return 'ok'
