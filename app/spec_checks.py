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

	max_res = max( result )

	print( result )

	if sum( result ) < 3:
		return 0
	elif sum( result ) >= 40:
		return -1
	else:
		repeat = result.count( max_res )
		start  = 0
		answer = ""

		if repeat > 1:
			for i in range( repeat ):
				start = result.index( max_res, start ) + 1
				answer += str( start )
				print( answer )

			return int( answer )

		else:
			return result.index( max_res ) + 1

