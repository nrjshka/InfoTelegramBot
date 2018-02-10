# -*- coding: utf-8 -*-

'''
@author: Max Korolev
@contact: nrjshka@gmail.com

Copyright (C) 2018
'''

from urllib.parse import urlparse
from flask import Flask, request, abort
from flask import Response
import re
import os
import json
import telebot
from infobot import *


bot = telebot.TeleBot(APP_CONFIG['TOKEN'])

app = Flask(__name__)

# Starting message
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Your message.', parse_mode="HTML")

# Telegram start point
@app.route("/bot", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# Main point of project
@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_CONFIG['TOKEN'])

    return "200 Status."

# Available, but not for heroku
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get("PORT", 5000)))
