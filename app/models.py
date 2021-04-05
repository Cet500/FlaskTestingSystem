from app import db


class Test(db.Model):
	id = db.Column( db.Integer, primary_key = True )

	def __repr__(self):
		return '<Test {}>'.format(self.id)
