#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
import telebot

class Index(APIView):
	''' Initializes the state of app at startup '''
	renderer_classes = {JSONRenderer, }
	
	def get(self, request, format = None):
		bot = telebot.TeleBot('463044045:AAHn0tjfG0TUngYED04KzRBvhujG6wvWnKE')
		bot.remove_webhook()
		bot.set_webhook(url = "https://informativebot.herokuapp.com/")

class Bot(APIView):
	''' Initializes a web hook for a telegram '''
	renderer_classes = {JSONRenderer, }

	def post(self, request, format = None):
		print('There was an update')
		return Response(True)