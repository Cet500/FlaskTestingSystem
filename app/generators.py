import random
import string


class Generators:
	def __init__(self):
		pass

	def random_string( self, length = 16, delta = 0, add_digits = False, add_space = False,
	                         only_uppercase = False, only_lowercase = False ):

		if only_uppercase:
			source = string.ascii_uppercase
		elif only_lowercase:
			source = string.ascii_lowercase
		else:
			source = string.ascii_letters

		if add_digits:
			source += string.digits

		if add_space:
			source += string.whitespace

		return self._get_string( source, length, delta )

	def random_rus_string( self, length = 16, delta = 0, add_digits = False, add_space = False,
	                             only_uppercase = False, only_lowercase = False ):

		if only_uppercase:
			source = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
		elif only_lowercase:
			source = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
		else:
			source = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

		if add_digits:
			source += string.digits

		if add_space:
			source += string.whitespace

		return self._get_string( source, length, delta )

	def random_int( self, min_int = 0, max_int = 1 ):
		return random.randint( min_int, max_int )

	def _get_string( self, source, length, delta ):
		if delta > 0:
			min_int = length - delta
			max_int = length + delta
			rand_string = ''.join( random.choices( source, k = random.randint( min_int, max_int ) ) )
		else:
			rand_string = ''.join( random.choices( source, k = length ) )

		return rand_string
