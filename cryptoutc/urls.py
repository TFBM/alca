#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views as auth_views
from manageuser.forms import AuthenticationForm

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^administration/', include(admin.site.urls)),

    url(r'^/?', include('home.urls')),
    url(r'^accounts/', include('manageuser.urls')),
)

urlpatterns += staticfiles_urlpatterns()
