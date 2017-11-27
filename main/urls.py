#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.contrib import admin
from .views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('api.urls')),
    url(r'^bot', Bot.as_view()),
    url(r'^', Index.as_view()),
]
