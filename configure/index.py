# -*- coding: utf-8 -*-
import os

token = os.environ['TELEGRAM_TOKEN']
server_url = "https://"+os.environ['HEROKU_APP_NAME'] + ".herokuapp.com"
print(server_url)