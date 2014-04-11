#-*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^administration/', include(admin.site.urls)),
    
    #Every other url goes to the home module
    url(r'^/?', include('home.urls')),
)

urlpatterns += staticfiles_urlpatterns()
