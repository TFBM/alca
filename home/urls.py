from django.conf.urls import patterns, url

urlpatterns = patterns('home.views',
    url(r'^/?$', 'home', name='home'),
    url(r'^profil/?$', 'profil', name='profil'),
    url(r'^profil/edit/?$', 'edit', name='edit'), 
    url(r'^profil/add/?$', 'add', name='add'), 
    url(r'^transactions/?$', 'transactions', name='transactions'),
    url(r'^disputes/?$', 'disputes', name='disputes'),
    url(r'^profil/new/?$', 'new', name='new'), 
)
