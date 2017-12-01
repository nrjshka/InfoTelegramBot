# -*- coding: utf-8 -*-

from flask_cors import CORS, cross_origin
from flask import Response
from urllib.parse import urlparse 
import re
import os
import json
import telebot
import configure.index as config
from flask import Flask, request, abort
import db
import configure.const as const	
import urllib

bot = telebot.TeleBot(config.token)
	
app = Flask(__name__)
CORS(app, supports_credentials=True)

# Starting message
@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, '<strong> ' + message.from_user.first_name + ', cпасибо, что установили нашего бота! ✌️</strong>\n\nVkFeedBot создан для работы ленты VK внутри Telegram.', parse_mode="HTML")
	db.addUser(message.chat.id)
	bot.send_message(int(message.chat.id), getCommandList(), parse_mode="HTML")


# Bot help
@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(int(message.chat.id), getCommandList(), parse_mode="HTML")


# 'addlink' method
@bot.message_handler(commands=['addlink'])
def addlink(message):
	bot.send_message(message.chat.id, "Введите URL группы, которую Вы хотели бы добавить?")
	db.changeStatus(message.chat.id, const.status[const.ADDING_LINK])


# 'removelink' method
@bot.message_handler(commands=['removelink'])
def removelink(message):
	bot.send_message(message.chat.id, "Введите URL группы, которую Вы хотели бы удалить?")
	db.changeStatus(message.chat.id, const.status[const.REMOVING_LINK])


# Checking all text
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
	# Getting status
	status = db.getStatus(message.chat.id)
	if status == const.status[const.UNACTIVE]:
		# If user is 'unactive'
		bot.send_message(message.chat.id, "Ась?Не слышу!")

	elif status == const.status[const.ADDING_LINK]:
		message.text = message.text.lower()

		if message.text == "отмена":
			# If the cancel the action
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			bot.send_message(message.chat.id, "Добавление группы отменено.")
			return 

		# If a person wants to add a group, then you need to analyze it and display the answer
		if checkURL(message.text):
			# Changinst status + add a group
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			
			# Checking status
			linkStatus = db.addLink(pathParser(message.text).path[1:], message.chat.id)
			if linkStatus == 0:
				# "All" is ok
				bot.send_message(message.chat.id, "Группа успешно добавлена ✅")
			elif linkStatus == 1:
				bot.send_message(message.chat.id, "Группа уже была добавлена")
			elif linkStatus == -1:
				bot.send_message(message.chat.id, "Произошла ошибка во время добавления группы")

		else:
			bot.send_message(message.chat.id, "Проверьте правильность введенный данных.\nДля выхода введите <strong>'Отмена'</strong>", parse_mode="HTML")

	elif status == const.status[const.REMOVING_LINK]:
		message.text = message.text.lower()

		if message.text == "отмена":
			# If we canceled all actions
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			bot.send_message(message.chat.id, "Добавление группы отменено.")
			return 

		# If a person wants to delete a group, then you need to analyze it and display a response
		if checkURL(message.text):
			# Changes the status, if it finds a group, then deletes it
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])

			linkStatus = db.removeLink(pathParser(message.text).path[1:])
			
			if linkStatus == 0:
				# All is ok
				bot.send_message(message.chat.id, "Группа успешно удалена ✅")
			elif linkStatus == 1:
				# Did not find such a group
				bot.send_message(message.chat.id, "Такой группы нет 😲")
			elif linkStatus == -1:
				# If error
				bot.send_message(message.chat.id, "Произошла ошибка во время добавления группы")				
			
		else:
			bot.send_message(message.chat.id, "Проверьте правильность введенный данных.\nДля выхода введите <strong>'Отмена'</strong>", parse_mode="HTML")

	else:
		bot.send_message(message.chat.id, "Ась?Не слышу!")


def checkURL(url):
	result = pathParser(url)
	if result.path != "" and 'vk.com' in result.netloc:
		return True
	else:
		return False

def pathParser(url):
	# We check for correspondence to the url string
	if '//' not in url:
		url = '%s%s' % ('http://', url)

	return urlparse(url)

# Help list
def getCommandList():
	return "<strong>Команды бота:</strong>" + "\n\n" + "<a>/addlink</a> - Добавить группу VK\n" + "<a>/removelink</a> - Удалить группу VK"

''' 
	Near goes app work
'''

@app.route("/bot", methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200


@app.route("/getsubs", methods=['POST', 'OPTIONS'])
@cross_origin()
def sendGroups():
	''' Sending group data '''
	result = db.getSubs()
	
	# If where was an error 
	if result == -1:
		abort(400)

	return json.dumps(result)

@app.route("/setupdates", methods=['POST', 'OPTIONS'])
@cross_origin()
def setupdates():
	''' The input receives the data of the group that you want to update '''
	content = request.get_json()

	for post in content['content']: 
		users = db.update(post, content['url'])
		for user in users:
			bot.send_message(user, "<strong>Поступило обновление с {}:</strong> \n\n {} \n\n {}".format(content['title'], post['text'], post['url']), parse_mode="HTML")
				
				
	return json.dumps({'status': 'ok'})

@app.route("/")
def webhook():
	bot.remove_webhook()
	# app url
	bot.set_webhook(url=config.token)
	membsers = db.getCount("users")
	subs = db.getCount("subs")

	return "<strong>Количество пользователей:</strong> {}<br> <strong>Количество групп:</strong> {}".format(membsers, subs) , 200

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
