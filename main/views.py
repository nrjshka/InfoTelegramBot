#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.views.generic import TemplateView

class Index(TemplateView):
	#при любых "вопросах" выводить index.html
	template_name = 'index/index.html'