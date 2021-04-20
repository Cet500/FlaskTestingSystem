def check_test_9( questions ):
	# Это отлаженная функция, работающая на захардкоденных
	# значениях вопросов теста в базе данных ( и магии )
	# Двойной цикл требуется для сдвига по вариантам ответов,
	# таковы правила проверки теста

	result = [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ]

	for i in range( 64, 73 ):
		for j in range( 0, 5 ):
			id = i + ( 9 * j )

			if int( questions[ str( id ) ] ) % 2 != 0:
				result[ i - 64 ] = result[ i - 64 ] + 1

	answer = result.index( max(result) ) + 1

	return answer
