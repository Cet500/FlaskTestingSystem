from flask import render_template, url_for, redirect, request
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _
from flask_babel import lazy_gettext as _l
from app import app, db, moment
from app.models import User, Group, Test
from app.forms import LoginForm, RegisterForm, AddGroupForm, AddTestForm


# ------------------------ main pages ------------------------ #


@app.route('/')
@app.route('/index')
def index():
	groups = Group.query.all()

	return render_template( "index.html", title = _("All tests"), menu = _("Test by groups"), groups = groups )


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


@app.route('/testing/<int:id>')
def testing(id):
	test  = Test.query.get(id)
	group = Group.query.get(test.id_group)

	link0 = url_for( 'index' )
	link1 = url_for( 'group', id = group.id )
	path  = f"<a href={link0}>Все тесты</a> / <a href={link1}>{group.title}</a> / {test.name}"

	return render_template( "test.html", title = f"{test.name}", path = path, test = test )


# ------------------------ login system ------------------------ #


@app.route('/login', methods = [ 'GET', 'POST' ])
def login():
	if current_user.is_authenticated:
		return redirect( url_for( "index" ) )

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by( username = form.username.data ).first()

		if user is None or not user.check_password( form.password.data ):
			return redirect( url_for( "login" ) )

		login_user( user, remember = form.remember_me.data )

		return redirect( '/index' )

	return render_template( "login.html", title = _("Sign in"), form = form )


@app.route('/register', methods = [ 'GET', 'POST' ])
def register():
	if current_user.is_authenticated:
		return redirect( url_for("index") )

	form = RegisterForm()

	if form.validate_on_submit():
		user = app.models.User( username = form.username.data, name = form.name.data, lastname = form.lastname.data,
		                        group = form.group.data, role = form.role.data )
		user.set_password( password = form.password.data )

		db.session.add( user )
		db.session.commit()

		return redirect( url_for( "index" ) )

	return render_template( "register.html", title = _( "Register" ), form = form )


@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for( "index" ) )


# ------------------------ forms pages ------------------------ #


@app.route('/add_group', methods = [ 'GET', 'POST' ])
def add_group():
	form = AddGroupForm()

	if form.validate_on_submit():
		group = Group( title = form.title.data, description = form.description.data )

		db.session.add( group )
		db.session.commit()

		last_insert_id = group.id

		return redirect( url_for( "group", id = last_insert_id ) )

	return render_template( "add-group.html", title = _( "Add group" ), form = form )


@app.route('/add_test', methods = [ 'GET', 'POST' ])
def add_test():
	groups = db.session.query( Group ).all()
	groups_list = [ ( g.id, g.title ) for g in groups ]

	form = AddTestForm()
	form.id_group.choices = groups_list

	if form.validate_on_submit():
		test = Test( id_group = form.id_group.data, name = form.name.data, annotation = form.annotation.data,
		             description = form.description.data )

		db.session.add( test )
		db.session.commit()

		last_insert_id = test.id

		return redirect( url_for( "test", id = last_insert_id ) )

	return render_template( "add-test.html", title = _( "Add test" ), form = form )


# ------------------------ technical pages ------------------------ #


@app.errorhandler(404)
def error_404(e):
	path = _('Errors') + " / 400 / " + _('Error 404')

	return render_template( "404.html", title = _('Error 404'), path = path ), 404


@app.errorhandler(405)
def error_405(e):
	path = _('Errors') + " / 400 / " + _('Error 405')

	return render_template( "405.html", title = _('Error 405'), path = path ), 405


@app.errorhandler(500)
def error_500(e):
	path = _('Errors') + " / 500 / " + _('Error 500')

	return render_template( "500.html", title = _('Error 500'), path = path ), 500


# ------------------------ test pages ------------------------ #


@app.route('/add')
def add():
	return 'ok'
