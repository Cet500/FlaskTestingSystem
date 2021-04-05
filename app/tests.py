import pytest
import os
from app import app, db
from app.models import Test, Question, Answer
from app.generators import Generators


ITER = 10
DROP = True


def setup_module():
	basedir = os.path.abspath( os.path.dirname( __file__ ) )
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join( basedir, 'test.db' )
	db.create_all()


def teardown_module():
	if DROP:
		db.session.remove()
		db.drop_all()
	else:
		pass


def test_add_tests():
	g = Generators()

	for i in range( ITER ):
		name = g.random_string( 20, 10 )
		description = g.random_string( 200, 50 )

		t = Test( name = name, description = description )

		db.session.add(t)
		db.session.commit()


def test_add_quests():
	g = Generators()

	for i in range( 1, ITER + 1 ):
		for j in range( ITER ):
			text = g.random_string( 200, 50 )

			q = Question( id_test = i, text = text )

			db.session.add(q)

		db.session.commit()


def test_add_answers():
	g = Generators()

	for i in range( 1, ( ITER * ITER ) + 1 ):
		for j in range( ITER ):
			text = g.random_string( 200, 50 )

			a = Answer( id_question = i, text = text )

			db.session.add(a)

		db.session.commit()
