# -*- coding: utf-8 -*-

# Подключаем бд
import sqlite3
import time

def addUser(id):
	''' 
		Проверяет существует пользователь или нет, 
		если нет - то добавляет в бд 
	'''

	# Отвечает за подключение к базе данных
	conn = sqlite3.connect("db.sqlite3")
	
	cursor = conn.cursor()

	# Ищет пользователя с подключенным id
	cursor.execute("SELECT * FROM users WHERE tgID = " + str(id))

	result = cursor.fetchall()

	if len(result) == 0:
		# Если пользователь новый, то нужно его добавить
		try:
			# Добавляем поле 
			cursor.execute("INSERT INTO users ('tgID') VALUES (?)" , [id, ])
			conn.commit()
		except:
			raise Exception('Adding Error')
			conn.rollback()

	conn.close()		 

def changeStatus(id, status):
	''' Меняет статус пользователя на отправленный '''
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Обновляем статус
		cursor.execute("UPDATE users SET status = ? WHERE tgID = ?", [status, id])
		conn.commit()
	except:
		raise Exception('Changing status error')
		conn.rollback()

	conn.close()

def getStatus(id):
	''' Выдает статус пользователя с tgId = id '''
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Получаем статус
		cursor.execute("SELECT status FROM users WHERE tgID = ?", [id])
		# Получаем результат
		result = cursor.fetchone()
		conn.close()
		# Отправляем статус(он идет третьим)
		return result[0]
	except:
		raise Exception('Getting error status')

		conn.close()
		# -1 - ошибка при выполнении
		return -1

def addLink(url, id):
	''' 
		Добавляет ссылку в базу данных 
		0 - успешно добавлено
		1 - уже было добавлено
		-1 - error code
	'''
	
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Проверяем есть ли такая ссылка
		cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
		result = cursor.fetchall()
		# Если уже есть такая ссылка
		if len(result) > 0:
			linkId = result[0][0]
			print(linkId)
			try:
				# Получаем id пользователя
				cursor.execute("SELECT id FROM users WHERE tgId = ?", [id])
				userId = cursor.fetchall()[0][0]
					
				cursor.execute("SELECT * FROM connect WHERE link = ? AND user = ?", [linkId, userId])

				result = cursor.fetchall()
				if len(result) > 0:
					# Если группа пользователем уже была добавлена
					conn.close()
					return 1
				else:
					
					# Добавляем группу
					cursor.execute("INSERT INTO connect (link, user) VALUES (?, ?)", [linkId, userId])
					conn.commit()
					conn.close()
					return 0

			except:
				raise Exception('Adding URL error')
				conn.rollback()
				conn.close()
				
				return -1

		# Добавляем данные
		try:
			# Добавляем URL группы в базу данных
			cursor.execute("INSERT INTO subs (link, lastTimeChanged) VALUES (?, ?)", [url, int(time.time())])
			conn.commit()
			
			# Получаем id добавленной группы
			cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
			linkId = cursor.fetchall()[0][0]

			# Получаем id пользователя
			cursor.execute("SELECT id FROM users WHERE tgId = ?", [id])
			userId = cursor.fetchall()[0][0]

			# Добавляем группу

			cursor.execute("INSERT INTO connect (link, user) VALUES (?, ?)", [linkId, userId])
			conn.commit()
			
			conn.close()

			return 0
		except:
			raise Exception('Adding URL error')
			conn.rollback()
			conn.close()
			
			return -1

	except:
		raise Exception('Checking link error')
		conn.rollback()
		conn.close()
		return -1

def removeLink(url):
	"""
		Удаляет ссылку из базы данных
		0 - удалено успешно
		1 - такой группы нет
		-1 - произошла ошибка 
	"""

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		# Проверяем существует ли эта группа
		cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
		# Парсим результат
		result = cursor.fetchall()
		if len(result) == 1:
			# Все идет по плану
			cursor.execute("DELETE FROM subs WHERE link = ?", [url])
			conn.commit()
			conn.close()

			return 0

		else:
			# Все катиться в ...
			conn.close()

			return 1
	except:
		conn.rollback()
		conn.close()

		return -1


def getSubs():
	''' Выдает сериализованные подписки '''

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT link, lastTimeChanged FROM subs")
		result = cursor.fetchall()

		return result
	except:
		# Все плохо
		conn.close()

		return -1


def getCount(pol):
	''' Выдает количество в таблице pol '''

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT COUNT(id) FROM {}".format(pol))

		return cursor.fetchall()[0][0]
	except:
		# Все плохо

		return -1


def update(content, url):
	''' Выдает список людей, у которых нужно обновить контент '''

	# Нужно пофиксить это дерьмо
	time = content['time']

	outputArray = []

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT id FROM subs WHERE link = ?", [url])

		idUrl = cursor.fetchall()[0][0]


		cursor.execute("UPDATE subs SET lastTimeChanged = ? WHERE link = ?", [str(time), str(url)])
		conn.commit()

		cursor.execute("SELECT user FROM connect WHERE link = ?", [idUrl])

		result = cursor.fetchall()
		for arr in result:
			user = arr[0]
			
			cursor.execute("SELECT tgId FROM users WHERE id = ?", [user])

			tgResult = cursor.fetchall()

			outputArray.append(tgResult[0][0])

		conn.close()
		return outputArray
	except:
		raise Exception('Updating groups error')
		conn.close()
		return -1