from app import db, login
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Group(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	title        = db.Column( db.String(32), index = True, unique = True, nullable = False )
	description  = db.Column( db.String(256) )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	tests = db.relationship( 'Test', backref = "tests", lazy = "dynamic" )

	def __repr__(self):
		return f'<group {self.title}>'


class Test(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	id_group     = db.Column( db.Integer, db.ForeignKey( 'group.id' ), nullable = False )
	name         = db.Column( db.String(32), index = True, unique = True, nullable = False )
	annotation   = db.Column( db.String(128) )
	description  = db.Column( db.String(512) )
	image        = db.Column( db.Integer )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	questions = db.relationship( 'Question', backref = "questions", lazy = "dynamic" )
	results   = db.relationship( 'Result', backref = "results", lazy = "dynamic" )

	def __repr__(self):
		return f'<test {self.name}>'


class Question(db.Model):
	id      = db.Column( db.Integer, primary_key = True )
	id_test = db.Column( db.Integer, db.ForeignKey( 'test.id' ), nullable = False )
	text    = db.Column( db.String(256), nullable = False )

	answers = db.relationship( 'Answer', backref = "answers", lazy = "dynamic" )

	def __repr__(self):
		return f'<question {self.text}>'

	def true_answer( self ):
		return self.answers.filter( Answer.is_true == True ).first().id


class Answer(db.Model):
	id          = db.Column( db.Integer, primary_key = True )
	id_question = db.Column( db.Integer, db.ForeignKey( 'question.id' ), nullable = False )
	text        = db.Column( db.String(256), nullable = False )
	is_true     = db.Column( db.Boolean, default = False )

	def __repr__(self):
		return f'<answer {self.text}>'


class User(UserMixin, db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	username     = db.Column( db.String(32), index = True, unique = True, nullable = False )
	name         = db.Column( db.String(32), nullable = False )
	lastname     = db.Column( db.String(32) )
	group        = db.Column( db.String(16) )
	pass_hash    = db.Column( db.String(128), nullable = False )
	role         = db.Column( db.String(1) )
	datetime_reg = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	solved_tests = db.relationship( 'Result', backref = "solved_tests", lazy = "dynamic" )

	def __repr__( self ):
		return f'<user {self.username}>'

	def set_password( self, password ):
		self.pass_hash = generate_password_hash( password )

	def check_password( self, password ):
		return check_password_hash( self.pass_hash, password )


@login.user_loader
def load_user( user_id ):
	return User.query.get( int( user_id ) )


class Result(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	id_user      = db.Column( db.Integer, db.ForeignKey( 'user.id' ), nullable = True )
	id_test      = db.Column( db.Integer, db.ForeignKey( 'test.id' ), nullable = False )
	mark         = db.Column( db.Integer, nullable = False )
	score        = db.Column( db.Integer, nullable = False )
	quests       = db.Column( db.Integer, nullable = False )
	percent      = db.Column( db.Float,   nullable = False )
	datetime_add = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	def __repr__( self ):
		return f'<result {self.id}>'
