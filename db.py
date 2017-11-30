# -*- coding: utf-8 -*-

# Подключаем бд
import sqlite3
import time

def addUser(id):
	''' 
		Checks whether the user exists or not,
		if not - then adds to the database
	'''

	# DB connection
	conn = sqlite3.connect("db.sqlite3")
	
	cursor = conn.cursor()

	# Searching for users with id == param id
	cursor.execute("SELECT * FROM users WHERE tgID = " + str(id))

	result = cursor.fetchall()

	if len(result) == 0:
		# If user is new, we should add him
		try:
			# Add a field 
			cursor.execute("INSERT INTO users ('tgID') VALUES (?)" , [id, ])
			conn.commit()
		except:
			raise Exception('Adding Error')
			conn.rollback()

	conn.close()		 

def changeStatus(id, status):
	''' Changes the status of the user to the sent '''
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Updating the status
		cursor.execute("UPDATE users SET status = ? WHERE tgID = ?", [status, id])
		conn.commit()
	except:
		raise Exception('Changing status error')
		conn.rollback()

	conn.close()

def getStatus(id):
	''' Gives user status with tgId = id '''
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Getting status
		cursor.execute("SELECT status FROM users WHERE tgID = ?", [id])
		# Gettubs result
		result = cursor.fetchone()
		conn.close()
		# Sending status(he goes third)
		return result[0]
	except:
		raise Exception('Getting error status')

		conn.close()
		# -1 - run-time error
		return -1

def addLink(url, id):
	''' 
		Adds a link to the database
		0 - success adding
		1 - has already been added
		-1 - error code
	'''
	
	conn = sqlite3.connect("db.sqlite3")

	cursor = conn.cursor()
	try:
		# Check is there a suck link
		cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
		result = cursor.fetchall()
		
		if len(result) > 0:
			linkId = result[0][0]
			print(linkId)
			try:
				# Getting user id
				cursor.execute("SELECT id FROM users WHERE tgId = ?", [id])
				userId = cursor.fetchall()[0][0]
					
				cursor.execute("SELECT * FROM connect WHERE link = ? AND user = ?", [linkId, userId])

				result = cursor.fetchall()
				if len(result) > 0:
					# If group has already been added
					conn.close()
					return 1
				else:
					
					# Adding a group 
					cursor.execute("INSERT INTO connect (link, user) VALUES (?, ?)", [linkId, userId])
					conn.commit()
					conn.close()
					return 0

			except:
				raise Exception('Adding URL error')
				conn.rollback()
				conn.close()
				
				return -1

		# Adding a data
		try:
			# Add a group URL to the database
			cursor.execute("INSERT INTO subs (link, lastTimeChanged) VALUES (?, ?)", [url, int(time.time())])
			conn.commit()
			
			# Get the id of the added group
			cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
			linkId = cursor.fetchall()[0][0]

			# Getting user id
			cursor.execute("SELECT id FROM users WHERE tgId = ?", [id])
			userId = cursor.fetchall()[0][0]

			# Adding a group

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
		Removes a reference from the database
		0 - succes status
		1 - there is not such group
		-1 - error status
	"""

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		# Check if this group exists
		cursor.execute("SELECT * FROM subs WHERE link = ?", [url])
		# Parse result
		result = cursor.fetchall()
		if len(result) == 1:
			# All is ok
			cursor.execute("DELETE FROM subs WHERE link = ?", [url])
			conn.commit()
			conn.close()

			return 0

		else:
			# All is not ok
			conn.close()

			return 1
	except:
		conn.rollback()
		conn.close()

		return -1


def getSubs():
	''' Gives serialized subscriptions '''

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT link, lastTimeChanged FROM subs")
		result = cursor.fetchall()

		return result
	except:
		# Fuck...
		conn.close()

		return -1


def getCount(pol):
	''' Returning a count of pol '''

	conn = sqlite3.connect("db.sqlite3")
	cursor = conn.cursor()
	try:
		cursor.execute("SELECT COUNT(id) FROM {}".format(pol))

		return cursor.fetchall()[0][0]
	except:
		# Fuck

		return -1


def update(content, url):
	''' List the people who need to update the content '''

	# FIX: need to fix
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