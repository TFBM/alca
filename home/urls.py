from django.conf.urls import patterns, url

urlpatterns = patterns('home.views',
    url(r'^/?$', 'home', name='home'),
    url(r'^test/?$', 'test', name='test'),
    url(r'^profil/?$', 'profil', name='profil'),
)
