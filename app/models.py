from app import db, login
from app.tokens import Tokens
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func


# ------------------------ Tests block ------------------------ #


class Group(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	title        = db.Column( db.String(32), index = True, unique = True, nullable = False )
	description  = db.Column( db.String(256) )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	tests = db.relationship( 'Test', backref = "tests", lazy = "dynamic" )

	def __repr__( self ):
		return f'<group {self.title}>'


class Test(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	id_group     = db.Column( db.Integer, db.ForeignKey( 'group.id' ), nullable = False )
	name         = db.Column( db.String(32), index = True, unique = True, nullable = False )
	annotation   = db.Column( db.String(128) )
	description  = db.Column( db.String(512) )
	image        = db.Column( db.Integer )
	difficult    = db.Column( db.Integer )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	questions = db.relationship( 'Question', backref = "questions", lazy = "dynamic" )
	results   = db.relationship( 'Result', backref = "results", lazy = "dynamic" )
	resumes   = db.relationship( 'TestResume', backref = "resumes", lazy = "dynamic" )

	def __repr__(self):
		return f'<test {self.name}>'

	def sum_marks( self ):
		return Result.query.with_entities( func.sum( Result.mark ).label('sum') ).filter( Result.id_test == self.id ).first().sum

	def avg_marks( self, is_round = True ):
		marks = int( self.sum_marks() or 0 )
		count = self.results.count()

		try:
			result = marks / count
		except ZeroDivisionError:
			result = 0.0

		if is_round:
			return round( result, 1 )
		else:
			return result

	def get_description_mark( self, mark ):
		try:
			if mark > 10:
				mark = 10

			return TestResume.query.filter( TestResume.id_test == self.id, TestResume.mark == mark ).first().resume
		except:
			return ""

	def set_description_mark( self, mark, desc ):
		try:
			TestResume.query.filter( TestResume.id_test == self.id, TestResume.mark == mark ).first().resume = desc
		except:
			res = TestResume( id_test = self.id, mark = mark, resume = desc )

			db.session.add(res)
			db.session.commit()

	def is_usual( self ):
		if self.id == 9:
			return False
		else:
			return True

	def is_unusual( self ):
		if self.id == 9:
			return True
		else:
			return False

	def print( self, data ):
		print( data )


class TestResume(db.Model):
	id      = db.Column( db.Integer, primary_key = True )
	id_test = db.Column( db.Integer, db.ForeignKey( 'test.id' ), nullable = False )
	mark    = db.Column( db.Integer, nullable = False )
	resume  = db.Column( db.String(512), nullable = False )

	def __repr__(self):
		return f'<resume of test {self.id_test} for mark {self.mark}>'


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


# ------------------------ Users block ------------------------ #


class Class(db.Model):
	id     = db.Column( db.Integer, primary_key = True )
	abbr   = db.Column( db.String(7), nullable = False )
	name   = db.Column( db.String(4) )
	course = db.Column( db.SmallInteger )
	number = db.Column( db.SmallInteger )
	datetime_reg = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	students = db.relationship( 'User', backref = "students", lazy = "dynamic" )

	def __repr__( self ):
		return f'<study class {self.abbr}>'


class User(UserMixin, db.Model):
	id            = db.Column( db.Integer, primary_key = True )
	id_class      = db.Column( db.Integer, db.ForeignKey( 'class.id' ), nullable = False )
	username      = db.Column( db.String(32), index = True, unique = True, nullable = False )
	name          = db.Column( db.String(32), nullable = False )
	lastname      = db.Column( db.String(32) )
	email         = db.Column( db.String(64), index = True, unique = True, nullable = False )
	pass_hash     = db.Column( db.String(128), nullable = False )
	description   = db.Column( db.String(256) )
	sex           = db.Column( db.String(1), default = 'N' )
	role          = db.Column( db.String(1) )
	datetime_last = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	datetime_reg  = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	datetime_upd  = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	solved_tests = db.relationship( 'Result', backref = "solved_tests", lazy = "dynamic" )

	def __repr__( self ):
		return f'<user {self.username}>'

	def set_password( self, password ):
		self.pass_hash = generate_password_hash( password )

	def check_password( self, password ):
		return check_password_hash( self.pass_hash, password )

	def get_class( self ):
		return Class.query.get( self.id_class ).abbr

	def get_reset_password_token( self ):
		t = Tokens()
		return t.encode( { "task": "reset_password", "id": self.id  } )

	@staticmethod
	def verify_reset_password_token( token ):
		t = Tokens()
		data = t.decode( token )

		if data["task"] == "reset_password":
			return User.query.get( data["id"] )


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

	def len_mark( self ):
		return len( str( self.mark ) )

	def get_int_mark( self, index ):
		return int( str( self.mark )[ index ] )


# ------------------------ Logs block ------------------------ #


class LogRequest(db.Model):
	id              = db.Column( db.Integer, primary_key = True )
	ip              = db.Column( db.String(15) )
	port            = db.Column( db.Integer )
	url             = db.Column( db.String(100) )
	datetime        = db.Column( db.DateTime, index = True, default = datetime.utcnow() )
	browser_family  = db.Column( db.String(50) )
	browser_name    = db.Column( db.String(50) )
	browser_version = db.Column( db.String(50) )
	device_type     = db.Column( db.String(50) )
	device_family   = db.Column( db.String(50) )
	device_name     = db.Column( db.String(50) )
	device_manufact = db.Column( db.String(50) )
	os_family       = db.Column( db.String(50) )
	os_name         = db.Column( db.String(50) )
	os_version      = db.Column( db.String(50) )
	os_platform     = db.Column( db.String(20) )
	screen_width    = db.Column( db.Integer )
	screen_height   = db.Column( db.Integer )
	screen_depth    = db.Column( db.Integer )


class LogClick(db.Model):
	id       = db.Column( db.Integer, primary_key = True )
	ip       = db.Column( db.String(15) )
	url      = db.Column( db.String(100) )
	click_x  = db.Column( db.Integer )
	click_y  = db.Column( db.Integer )
	datetime = db.Column( db.DateTime )
