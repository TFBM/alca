#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^administration/', include(admin.site.urls)),    

    url(r'^/?$', 'home.views.home', name='home'),
    url(r'^profil/?', include('home.urls')),
    url(r'^transactions/?', include('transactions.urls')),
    url(r'^accounts/', include('manageuser.urls')),
)

urlpatterns += staticfiles_urlpatterns()
