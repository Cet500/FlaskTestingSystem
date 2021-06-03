from flask_wtf import FlaskForm
from flask_babel import _
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, RadioField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import IntegerRangeField
from app.models import User
import re


class EmptyForm(FlaskForm):
	submit = SubmitField( _l("Submit") )


class LoginForm(FlaskForm):
	username    = StringField(   _l("Username"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	password    = PasswordField( _l("Password"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	remember_me = BooleanField(  _l("Remember me") )
	submit      = SubmitField(   _l("Sign in") )


class RegisterForm(FlaskForm):
	name      = StringField( _l("Name"), validators = [ DataRequired(), Length( min = 2, max = 32 ) ] )
	lastname  = StringField( _l("Lastname"), validators = [ DataRequired(), Length( min = 2, max = 32 ) ] )
	username  = StringField( _l("Username"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	email     = StringField( _l("Email"), validators = [ DataRequired(), Email(), Length( min = 7, max = 64  ) ] )
	id_class  = SelectField( _l("Group"), coerce = int,  validators = [ DataRequired() ] )
	role      = SelectField( _l("Role"), choices = [ ( "S", _l("Student") ), ( "T", _l("Teacher") ) ],
	                                     validators = [ DataRequired() ] )
	password  = PasswordField( _l("Password"), validators = [ DataRequired(), Length( min = 8, max = 64 ) ] )
	password2 = PasswordField( _l("Repeat password"), validators = [ DataRequired(), EqualTo( 'password' ) ] )
	submit    = SubmitField( _l("Register") )

	def validate_username( self, username ):
		user = User.query.filter_by( username = username.data ).first()

		if user is not None:
			raise ValidationError( _l("Please use a different login") )

		if re.search( '\W', username.data ):
			raise ValidationError( _l("Use only A-Z, a-z, 0-9 and _") )

	def validate_email( self, email ):
		user = User.query.filter_by( email = email.data ).first()
		if user is not None:
			raise ValidationError( _l("Please use a different email") )

	def validate_password( self, password ):
		if re.search('[a-z]', password.data) is None:
			raise ValidationError( _l("Use letter in password") )

		if re.search('[A-Z]', password.data) is None:
			raise ValidationError( _l("Use capital in password") )

		if re.search('[0-9]', password.data) is None:
			raise ValidationError( _l("Use number in password") )


class GroupForm(FlaskForm):
	title       = StringField( _l("Title"), validators = [ DataRequired(), Length( min = 4, max = 32 ) ] )
	description = TextAreaField( _l("Description"), validators = [ DataRequired(), Length( min = 16, max = 256 ) ] )


class AddGroupForm(GroupForm):
	submit = SubmitField( _l( "Add group" ) )


class UpdateGroupForm(GroupForm):
	submit = SubmitField( _l( "Update group" ) )


class TestForm(FlaskForm):
	id_group    = SelectField( _l("Group"), coerce = int, validators = [ DataRequired() ] )
	name        = StringField( _l("Name of test"), validators = [ DataRequired(), Length( min = 4, max = 32 ) ] )
	annotation  = TextAreaField( _l("Annotation of test"), validators = [ DataRequired(), Length( min = 16, max = 128 ) ] )
	description = TextAreaField( _l("Description of test"), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )


class AddTestForm(TestForm):
	submit = SubmitField( _l( "Add test" ) )


class UpdateTestForm(TestForm):
	difficult     = IntegerRangeField( _l( "Difficult of test" ), validators = [ DataRequired() ] )
	# test_resume_5 = TextAreaField( _l( "Test resume for mark '5'" ), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )
	# test_resume_4 = TextAreaField( _l( "Test resume for mark '4'" ), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )
	# test_resume_3 = TextAreaField( _l( "Test resume for mark '3'" ), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )
	# test_resume_2 = TextAreaField( _l( "Test resume for mark '2'" ), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )
	submit        = SubmitField( _l( "Update test" ) )


class UpdateProfileForm(TestForm):
	name = StringField( _l( "Name" ), validators = [DataRequired(), Length( min = 2, max = 32 )] )
	lastname = StringField( _l( "Lastname" ), validators = [DataRequired(), Length( min = 2, max = 32 )] )
	username = StringField( _l( "Username" ), validators = [DataRequired(), Length( min = 3, max = 32 )] )
	description = TextAreaField( _l( "Description" ), validators = [DataRequired(), Length( min = 0, max = 256 )] )
	id_class = SelectField( _l( "Group" ), coerce = int, validators = [DataRequired()] )
	role = SelectField( _l( "Role" ), choices = [("S", _l( "Student" )), ("T", _l( "Teacher" ))],
	                    validators = [DataRequired()] )
	sex = RadioField( _l( "Sex" ), choices = [("M", _l( "Male" )), ("F", _l( "Female" )), ("N", _l( "None" ))],
	                               validators = [DataRequired()] )
	submit = SubmitField( _l( "Apply" ) )

	def __init__(self, orig_login, *args, **kwargs):
		super( UpdateProfileForm, self ).__init__(*args, **kwargs)
		self.orig_login = orig_login

	def validate_login( self, login ):
		if login.data != self.orig_login:
			user = User.query.filter_by( login = login.data ).first()
			if user is not None:
				raise ValidationError( _l("Please use a different login") )

			if re.search( '\W', login.data ):
				raise ValidationError( _l("Use only A-Z, a-z, 0-9 and _") )
