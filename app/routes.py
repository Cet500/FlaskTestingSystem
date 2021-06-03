import json

from flask import render_template, url_for, redirect, request, send_from_directory, g
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale
from flask_babel import lazy_gettext as _l
from wtforms import RadioField, TextAreaField
from wtforms.validators import DataRequired, Length
from app import app, db, moment
from app.models import Class, User, Group, Test, Result, TestResume
from app.forms import EmptyForm, LoginForm, RegisterForm, AddGroupForm, UpdateGroupForm, AddTestForm, UpdateTestForm
from app.spec_checks import check_test_9


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
	path = f"<a href='{link}'>{_('All tests')}</a> / {group.title}"

	return  render_template( "group.html", title = f"{group.title}", path = path, menu = "Тесты в группе", group = group )


@app.route('/test/<int:id>')
def test(id):
	test  = Test.query.get(id)
	group = Group.query.get(test.id_group)

	link0 = url_for( 'index' )
	link1 = url_for( 'group', id = group.id )
	path  = f"<a href={link0}>{_('All tests')}</a> / <a href={link1}>{group.title}</a> / {test.name}"

	return render_template( "test-base.html", title = test.name + " / " + _("Info"), path = path, test = test )


@app.route('/testing/<int:id>', methods = [ 'GET', 'POST' ])
def testing(id):
	test  = Test.query.get(id)
	group = Group.query.get(test.id_group)

	link0 = url_for( 'index' )
	link1 = url_for( 'group', id = group.id )
	path  = f"<a href={link0}>{_('All tests')}</a> / <a href={link1}>{group.title}</a> / {test.name}"

	class TestingForm(EmptyForm):
		pass

	for question in test.questions:
		setattr( TestingForm,
		         str(question.id),
		         RadioField( question.text, choices = [ ( a.id, a.text ) for a in question.answers ] ,
		                                    validators = [ DataRequired() ] ) )

	form = TestingForm()

	if form.validate_on_submit():
		arr     = form.data
		score   = -1
		mark    = 0
		quests  = test.questions.count()
		percent = -1

		if current_user.is_authenticated:
			id_user = current_user.id
		else:
			id_user = None

		if id != 9:
			# Checks usual tests

			score = 0

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

		elif id == 9:
			# Check test 9

			mark  = check_test_9( arr )

			print( mark )

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
	path  = f"<a href={link0}>{_('All tests')}</a> / <a href={link1}>{group.title}</a> / {test.name}"

	return render_template( "test-result.html", title = test.name + " / " + _("Result"), path = path, result = result,
	                                            test = test, user = user )


@app.route('/profile')
def profile():
	return render_template( "forms/profile.html", title = _( 'Profile' ) )


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

	classes = Class.query.all()
	classes_list = [ ( c.id, c.abbr ) for c in classes ]

	form = RegisterForm()
	form.id_class.choices = classes_list

	if form.validate_on_submit():
		user = User( username = form.username.data, name = form.name.data, lastname = form.lastname.data,
		             email = form.email.data, id_group = form.id_group.data, role = form.role.data )
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
		return redirect( url_for( "group", id = id ) )

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
	test = Test.query.get( id )

	class UpdateSpecTestForm(UpdateTestForm):
		pass

	min_key  = 0
	max_key  = 0
	name_key = ""

	if test.is_usual():
		min_key = 2
		max_key = 6
		name_key =  _l( "Test resume for mark " )
	else:
		if id == 9:
			min_key = -1
			max_key = 11
			name_key = _l( "Test resume for key " )

	for i in range( min_key, max_key ):
		setattr( UpdateSpecTestForm, f'test_resume_{i}',
		         TextAreaField( "{}'{}'".format( name_key, i ), validators = [DataRequired(), Length( min = 32, max = 512 )] ) )

	form = UpdateSpecTestForm()

	form.id_group.choices = groups_list

	if form.validate_on_submit():
		test.id_group    = form.id_group.data
		test.name        = form.name.data
		test.difficult   = form.difficult.data
		test.annotation  = form.annotation.data
		test.description = form.description.data

		for i in range(min_key, max_key):
			test.set_description_mark( i, form[ f'test_resume_{i}' ].data )

		db.session.commit()
		return redirect( url_for( "test", id = id ) )

	elif request.method == 'GET':
		form.id_group.data    = test.id_group
		form.name.data        = test.name
		form.difficult.data   = test.difficult
		form.annotation.data  = test.annotation
		form.description.data = test.description

		for i in range( min_key, max_key ):
			form[ f'test_resume_{i}' ].data = test.get_description_mark(i)

	return render_template( "forms/test-update.html", title = _('Change of test'), form = form,
	                                                  min_key = min_key, max_key = max_key )


# ------------------------ admin pages ------------------------ #


@app.route('/admin/tables')
def admin_tables():
	user   = User
	group  = Group
	test   = Test
	result = Result

	return render_template( "admin/tables.html", title = _('Admin-panel') + ' / ' + _('Tables'),
	                                             user = user, group = group, test = test, result = result )


@app.route('/admin/table/users')
def admin_table_users():
	users  = User.query.all()

	title = f"{_( 'Admin-panel' )} / {_( 'Tables' )} / {_( 'Users' )}"

	link0 = url_for( 'admin_tables' )
	path  = f"{_('Admin-panel')} / <a href='{link0}'>{_('Tables')}</a> / {_('Users')}"

	return render_template( "admin/table-users.html", title = title, path = path, users = users, wide = True )


@app.route('/admin/table/groups')
def admin_table_groups():
	groups  = Group.query.all()

	title = f"{_( 'Admin-panel' )} / {_( 'Tables' )} / {_( 'Groups' )}"

	link0 = url_for( 'admin_tables' )
	path = f"{_( 'Admin-panel' )} / <a href='{link0}'>{_( 'Tables' )}</a> / {_( 'Groups' )}"

	return render_template( "admin/table-groups.html", title = title, path = path, groups = groups, wide = True )


@app.route('/admin/table/tests')
def admin_table_tests():
	tests  = Test.query.all()

	title = _( 'Admin-panel' ) + ' / ' + _( 'Tables' ) + ' / ' + _( 'Tests' )

	link0 = url_for( 'admin_tables' )
	path = f"{_( 'Admin-panel' )} / <a href='{link0}'>{_( 'Tables' )}</a> / {_( 'Tests' )}"

	return render_template( "admin/table-tests.html", title = title, path = path, tests = tests, wide = True )


@app.route('/admin/table/results')
def admin_table_results():
	results  = Result.query.all()

	title = _( 'Admin-panel' ) + ' / ' + _( 'Tables' ) + ' / ' + _( 'Results' )

	link0 = url_for( 'admin_tables' )
	path = f"{_( 'Admin-panel' )} / <a href='{link0}'>{_( 'Tables' )}</a> / {_( 'Results' )}"

	return render_template( "admin/table-results.html", title = title, path = path, results = results, wide = True )


@app.route('/admin/statistic')
def admin_statistic():
	return render_template( "admin/statistic.html", title = _('Admin-panel') + ' / ' + _('Statistic') )


# ------------------------ API pages ------------------------ #


@app.route('/api')
def api():
	return render_template("api.html", title = _('API methods list'))


# --- users ---


@app.route('/api/get_users_count')
def api_get_users_count():
	count = User.query.count()

	return str( count )


# --- groups ---


@app.route('/api/get_groups_count')
def api_get_groups_count():
	count = Group.query.count()

	return str( count )


@app.route('/api/get_groups_list')
def api_get_groups_list():
	list = Group.query.all()
	arr  = []

	for item in list:
		arr.append( { 'id': item.id, 'title': item.title } )

	return json.dumps(arr)


# --- tests ---


@app.route('/api/get_tests_count')
def api_get_tests_count():
	count = Test.query.count()

	return str( count )


@app.route('/api/get_tests_list')
def api_get_tests_list():
	list = Test.query.all()
	arr = []

	for item in list:
		arr.append( { 'id': item.id, 'id_group': item.id_group, 'name': item.name } )

	return json.dumps( arr )


@app.route('/api/get_tests_count_by_group/<int:id>')
def api_get_tests_count_by_group(id):
	if Group.query.get( id ):
		count = Test.query.filter( Test.id_group == id ).count()
	else:
		count = 'null'

	return str( count )


@app.route('/api/get_tests_list_by_group/<int:id>')
def api_get_tests_list_by_group(id):
	if Group.query.get( id ):
		list = Test.query.filter( Test.id_group == id ).all()
		arr = []

		for item in list:
			arr.append( { 'id': item.id, 'id_group': item.id_group, 'name': item.name } )

		return json.dumps( arr )

	else:
		response = 'null'

	return str( response )


# --- results ---


@app.route('/api/get_results_count')
def api_get_results_count():
	count = Result.query.count()

	return str( count )


@app.route('/api/get_results_list')
def api_get_results_list():
	list = Result.query.all()
	arr = []

	for item in list:
		arr.append( { 'id': item.id, 'id_test': item.id_test, 'id_user': item.id_user, 'mark': item.mark } )

	return json.dumps( arr )


@app.route('/api/get_results_count_by_test/<int:id>')
def api_get_results_count_by_test(id):
	if Test.query.get( id ):
		count = Result.query.filter( Result.id_test == id ).count()
	else:
		count = 'null'

	return str( count )


# ------------------------ system pages ------------------------ #


@app.route('/about_system')
def about_system():
	return render_template( "about-system.html", title = _('About TeSi') )


@app.route('/about_us')
def about_us():
	return render_template( "about-us.html", title = _('About us') )


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

	return render_template( "errors/404.html", title = _( 'Error 404' ), path = path ), 404


@app.errorhandler(405)
def error_405(e):
	path = _('Errors') + " / 400 / " + _('Error 405')

	return render_template( "errors/405.html", title = _( 'Error 405' ), path = path ), 405


@app.errorhandler(500)
def error_500(e):
	path = _('Errors') + " / 500 / " + _('Error 500')

	return render_template( "errors/500.html", title = _( 'Error 500' ), path = path ), 500


@app.before_request
def before_request():
	g.locale = str( get_locale() )
	g.theme = 'dark'
