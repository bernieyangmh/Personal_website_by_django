__author__ = 'bernie yang'
# -*- coding:utf-8 -*-

from django.conf.urls import url
from rango import views
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^category/(?P<category_name_slug>[\w\-]+)/$', views.show_category, name='show_category'),
    url(r'^add_category/$', views.add_category, name='add_category'),
]