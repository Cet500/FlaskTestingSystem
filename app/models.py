from app import db
from datetime import datetime


class Group(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	title        = db.Column( db.String(32), index = True, unique = True, nullable = False )
	description  = db.Column( db.String(256) )
	image        = db.Column( db.Integer )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	tests = db.relationship( 'Test', backref = "tests", lazy = "dynamic" )

	def __repr__(self):
		return f'<Group {self.title}>'


class Test(db.Model):
	id           = db.Column( db.Integer, primary_key = True )
	id_group     = db.Column( db.Integer, db.ForeignKey( 'group.id' ), nullable = False )
	name         = db.Column( db.String(32), index = True, unique = True, nullable = False )
	description  = db.Column( db.String(256) )
	datetime_add = db.Column( db.DateTime, default = datetime.utcnow(), index = True )
	datetime_upd = db.Column( db.DateTime, default = datetime.utcnow(), onupdate = datetime.utcnow() )

	questions = db.relationship( 'Question', backref = "questions", lazy = "dynamic" )

	def __repr__(self):
		return f'<Test {self.name}>'


class Question(db.Model):
	id      = db.Column( db.Integer, primary_key = True )
	id_test = db.Column( db.Integer, db.ForeignKey( 'test.id' ), nullable = False )
	text    = db.Column( db.String(256), nullable = False )

	answers = db.relationship( 'Answer', backref = "answers", lazy = "dynamic" )

	def __repr__(self):
		return f'<Question {self.text}>'


class Answer(db.Model):
	id          = db.Column( db.Integer, primary_key = True )
	id_question = db.Column( db.Integer, db.ForeignKey( 'question.id' ), nullable = False )
	text        = db.Column( db.String(256), nullable = False )
	is_true     = db.Column( db.Boolean, default = False )

	def __repr__(self):
		return f'<Answer {self.text}>'
