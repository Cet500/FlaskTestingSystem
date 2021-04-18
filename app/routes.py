from flask import render_template, url_for, redirect, request, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _
from flask_babel import lazy_gettext as _l
from wtforms import RadioField
from wtforms.validators import DataRequired
from app import app, db, moment
from app.models import User, Group, Test, Result
from app.forms import EmptyForm, LoginForm, RegisterForm, AddGroupForm, UpdateGroupForm, AddTestForm, UpdateTestForm


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

	return render_template( "test-base.html", title = test.name + " / " + _("Info"), path = path, test = test )


@app.route('/testing/<int:id>', methods = [ 'GET', 'POST' ])
def testing(id):
	test  = Test.query.get(id)
	group = Group.query.get(test.id_group)

	link0 = url_for( 'index' )
	link1 = url_for( 'group', id = group.id )
	path  = f"<a href={link0}>Все тесты</a> / <a href={link1}>{group.title}</a> / {test.name}"

	class TestingForm(EmptyForm):
		pass

	for question in test.questions:
		setattr( TestingForm,
		         str(question.id),
		         RadioField( question.text, choices = [ ( a.id, a.text ) for a in question.answers ] ,
		                                    validators = [ DataRequired() ] ) )

	form = TestingForm()

	if form.validate_on_submit():
		arr    = form.data
		score  = 0
		mark   = 0
		quests = test.questions.count()

		if current_user.is_authenticated:
			id_user = current_user.id
		else:
			id_user = None

		# if id != 7

		for question in test.questions:
			if arr[ str(question.id) ] == str( question.true_answer() ):
				score += 1

		percent = round( ( score / quests ) * 100, 1 )

		if percent >= 90:
			mark = 5
		elif 75 < percent < 90:
			mark = 4
		elif 50 < percent <= 75:
			mark = 3
		elif percent <= 50:
			mark = 2

		print( mark )

		# else...

		result = Result( id_test = test.id, id_user = id_user, mark = mark, score = score, quests = quests, percent = percent )

		db.session.add( result )
		db.session.commit()

		last_insert_id = result.id

		return redirect( url_for( "result", id = last_insert_id ) )

	return render_template( "test.html", title = test.name + " / " + _("Testing"), path = path, form = form, test = test )


@app.route('/result/<int:id>')
def result(id):
	result = Result.query.get( id )
	test   = Test.query.get( result.id_test )
	group  = Group.query.get( test.id_group )

	if result.id_user is None:
		user = "None"
	else:
		user = User.query.get( result.id_user )

	link0 = url_for( 'index' )
	link1 = url_for( 'group', id = group.id )
	path  = f"<a href={link0}>Все тесты</a> / <a href={link1}>{group.title}</a> / {test.name}"

	return render_template( "test-result.html", title = test.name + " / " + _("Result"), path = path, result = result,
	                                            test = test, user = user )


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

		return redirect( url_for( "index" ) )

	return render_template( "login.html", title = _("Sign in"), form = form )


@app.route('/register', methods = [ 'GET', 'POST' ])
def register():
	if current_user.is_authenticated:
		return redirect( url_for("index") )

	form = RegisterForm()

	if form.validate_on_submit():
		user = User( username = form.username.data, name = form.name.data, lastname = form.lastname.data,
		             group = form.group.data, role = form.role.data )
		user.set_password( password = form.password.data )

		db.session.add( user )
		db.session.commit()

		return redirect( url_for( "login" ) )

	return render_template( "register.html", title = _( "Register" ), form = form )


@app.route('/logout')
def logout():
	logout_user()
	return redirect( url_for( "index" ) )


# ------------------------ forms pages ------------------------ #


@app.route('/add_group', methods = [ 'GET', 'POST' ])
@login_required
def add_group():
	form = AddGroupForm()

	if form.validate_on_submit():
		group = Group( title = form.title.data, description = form.description.data )

		db.session.add( group )
		db.session.commit()

		last_insert_id = group.id

		return redirect( url_for( "group", id = last_insert_id ) )

	return render_template( "forms/group-add.html", title = _( "Add group" ), form = form )


@app.route('/update_group/<int:id>', methods = [ 'GET', 'POST' ])
def update_group(id):
	form = UpdateGroupForm()

	group = Group.query.get( id )

	if form.validate_on_submit():
		group.title       = form.title.data
		group.description = form.description.data

		db.session.commit()
		return redirect( url_for( 'update_group', id = id ) )

	elif request.method == 'GET':
		form.title.data       = group.title
		form.description.data = group.description

	return render_template( "forms/group-update.html", title = _('Change of group'), form = form  )


@app.route('/add_test', methods = [ 'GET', 'POST' ])
@login_required
def add_test():
	groups = Group.query.all()
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

	return render_template( "forms/test-add.html", title = _( "Add test" ), form = form )


@app.route('/update_test/<int:id>', methods = ['GET', 'POST'])
@login_required
def update_test(id):
	groups = Group.query.all()
	groups_list = [(g.id, g.title) for g in groups]

	form = UpdateTestForm()
	form.id_group.choices = groups_list

	test = Test.query.get(id)

	if form.validate_on_submit():
		test.id_group    = form.id_group.data
		test.name        = form.name.data
		test.difficult   = form.difficult.data
		test.annotation  = form.annotation.data
		test.description = form.description.data

		db.session.commit()
		return redirect( url_for( 'update_test', id = id ) )

	elif request.method == 'GET':
		form.id_group.data    = test.id_group
		form.name.data        = test.name
		form.difficult.data   = test.difficult
		form.annotation.data  = test.annotation
		form.description.data = test.description

	return render_template( "forms/test-update.html", title = _('Change of test'), form = form )


# ------------------------ technical pages ------------------------ #


@app.route('/null')
def null():
	return "null"


@app.route('/favicon.ico')
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
	return send_from_directory(app.static_folder, request.path[1:])


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
