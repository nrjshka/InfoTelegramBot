# -*- coding: utf-8 -*-

from flask_cors import CORS, cross_origin
from flask import Response
from urllib.parse import urlparse 
import re
import os
import json
# Подключение либы для работы с телграмом
import telebot
# Подключение конфига
import configure.index as config
# Подключение фласка
from flask import Flask, request, abort
# Подключаем бд
import db
# Константы проекта
import configure.const as const	
import urllib

bot = telebot.TeleBot(config.token)
	
server = Flask(__name__)
CORS(server, supports_credentials=True)

# Cтартовое сообщение
@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, '<strong> ' + message.from_user.first_name + ', cпасибо, что установили нашего бота! ✌️</strong>\n\nVkFeedBot создан для работы ленты VK внутри Telegram.', parse_mode="HTML")
	db.addUser(message.chat.id)
	bot.send_message(int(message.chat.id), getCommandList(), parse_mode="HTML")


# Хелп бота
@bot.message_handler(commands=['help'])
def help(message):
	bot.send_message(int(message.chat.id), getCommandList(), parse_mode="HTML")


# Добавление группы VK
@bot.message_handler(commands=['addlink'])
def addlink(message):
	bot.send_message(message.chat.id, "Введите URL группы, которую Вы хотели бы добавить?")
	db.changeStatus(message.chat.id, const.status[const.ADDING_LINK])


# Удаление группы VK
@bot.message_handler(commands=['removelink'])
def removelink(message):
	bot.send_message(message.chat.id, "Введите URL группы, которую Вы хотели бы удалить?")
	db.changeStatus(message.chat.id, const.status[const.REMOVING_LINK])


# Проверка любого текста
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
	# Получаем статус
	status = db.getStatus(message.chat.id)
	if status == const.status[const.UNACTIVE]:
		# Если мы "неактивны"
		bot.send_message(message.chat.id, "Ась?Не слышу!")

	elif status == const.status[const.ADDING_LINK]:
		message.text = message.text.lower()

		if message.text == "отмена":
			# Если мы отменили действие
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			bot.send_message(message.chat.id, "Добавление группы отменено.")
			return 

		# Если человек хочет добавить группу, то нужно проанализировать ее и вывести отвеь
		if checkURL(message.text):
			# Меняем статус + добавляем ссылку
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			
			# Проверяем статус
			linkStatus = db.addLink(pathParser(message.text).path[1:], message.chat.id)
			if linkStatus == 0:
				# Все хорошо
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
			# Если мы отменили действие
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])
			bot.send_message(message.chat.id, "Добавление группы отменено.")
			return 

		# Если человек хочет удалить группу, то нужно проанализировать ее и вывести ответ
		if checkURL(message.text):
			# Меняет статус, если находит группу, то удаляет ее
			db.changeStatus(message.chat.id, const.status[const.UNACTIVE])

			linkStatus = db.removeLink(pathParser(message.text).path[1:])
			
			if linkStatus == 0:
				# Все прошло хорошо
				bot.send_message(message.chat.id, "Группа успешно удалена ✅")
			elif linkStatus == 1:
				# Не нашли такой группы
				bot.send_message(message.chat.id, "Такой группы нет 😲")
			elif linkStatus == -1:
				# Если произошла ошибка
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
	# Проверяем на соответствие url строке
	if '//' not in url:
		url = '%s%s' % ('http://', url)

	return urlparse(url)

# Выдает список команд
def getCommandList():
	return "<strong>Команды бота:</strong>" + "\n\n" + "<a>/addlink</a> - Добавить группу VK\n" + "<a>/removelink</a> - Удалить группу VK"

''' 
	Ниже идет работа с сервером
'''

@server.route("/bot", methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200


@server.route("/getsubs", methods=['POST', 'OPTIONS'])
@cross_origin()
def sendGroups():
	''' Отправляет данные группы '''
	result = db.getSubs()
	
	# Если была ошибка при выполнении 
	if result == -1:
		abort(400)

	return json.dumps(result)

@server.route("/setupdates", methods=['POST', 'OPTIONS'])
@cross_origin()
def setupdates():
	''' На вход получает данные группы, которые нужно обновить'''
	content = request.get_json()

	for post in content['content']: 
		users = db.update(post, content['url'])
		for user in users:
			bot.send_message(user, "<strong>Поступило обновление с {}:</strong> \n\n {} \n\n {}".format(content['title'], post['text'], post['url']), parse_mode="HTML")
				
				
	return json.dumps({'status': 'ok'})

@server.route("/")
def webhook():
	bot.remove_webhook()
	# Server url
	bot.set_webhook(url="https://onfeedvkbot.herokuapp.com/bot")
	membsers = db.getCount("users")
	subs = db.getCount("subs")

	return "<strong>Количество пользователей:</strong> {}<br> <strong>Количество групп:</strong> {}".format(membsers, subs) , 200

server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)