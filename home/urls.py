from django.conf.urls import patterns, url

urlpatterns = patterns('home.views',
    url(r'^$', 'profil', name='profil'),
    url(r'^edit/?$', 'edit', name='edit'), 
    url(r'^add/?$', 'add', name='add'), 
    url(r'^disputes?$', 'disputes', name='disputes'), 
)
