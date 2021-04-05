from flask import render_template, url_for
from app import app, db, moment


@app.route('/')
@app.route('/index')
def index():
    return render_template( "index.html", title = "Главная" )
