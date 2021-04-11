from flask_wtf import FlaskForm
from flask_babel import _
from flask_babel import lazy_gettext as _l
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SelectField, RadioField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User
import re


class LoginForm(FlaskForm):
	username    = StringField(   _l("Username"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	password    = PasswordField( _l("Password"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	remember_me = BooleanField(  _l("Remember me") )
	submit      = SubmitField(   _l("Sign in") )


class RegisterForm(FlaskForm):
	name      = StringField( _l("Name"), validators = [ DataRequired(), Length( min = 2, max = 32 ) ] )
	lastname  = StringField( _l("Lastname"), validators = [ DataRequired(), Length( min = 2, max = 32 ) ] )
	username  = StringField( _l("Username"), validators = [ DataRequired(), Length( min = 3, max = 32 ) ] )
	group     = StringField( _l("Group"), validators = [ Length( max = 8 ) ] )
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

	def validate_password( self, password ):
		if re.search('[a-z]', password.data) is None:
			raise ValidationError( _l("Use letter in password") )

		if re.search('[A-Z]', password.data) is None:
			raise ValidationError( _l("Use capital in password") )

		if re.search('[0-9]', password.data) is None:
			raise ValidationError( _l("Use number in password") )


class AddGroupForm(FlaskForm):
	title       = StringField( _l("Title"), validators = [ DataRequired(), Length( min = 4, max = 32 ) ] )
	description = TextAreaField( _l("Description"), validators = [ DataRequired(), Length( min = 16, max = 256 ) ] )
	submit      = SubmitField( _l("Add group") )


class AddTestForm(FlaskForm):
	id_group    = SelectField( _l("Group"), coerce = int, validators = [ DataRequired() ] )
	name        = StringField( _l("Name of test"), validators = [ DataRequired(), Length( min = 4, max = 32 ) ] )
	annotation  = TextAreaField( _l("Annotation of test"), validators = [ DataRequired(), Length( min = 16, max = 128 ) ] )
	description = TextAreaField( _l("Description of test"), validators = [ DataRequired(), Length( min = 32, max = 512 ) ] )
	submit      = SubmitField( _l( "Add test" ) )
