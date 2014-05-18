from django.conf.urls import patterns, url

urlpatterns = patterns('home.views',
    url(r'^/?$', 'home', name='home'),
    url(r'^profil/?$', 'profil', name='profil'),
    url(r'^profil/edit/?$', 'edit', name='edit'), 
    url(r'^transactions/?$', 'transactions', name='transactions'),
)
