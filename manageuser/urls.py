from django.conf.urls import patterns, url

urlpatterns = patterns('manageuser.views',
    url(r'^login/?$', 'login_view', name='login'),
    url(r'^logout/?$', 'logout_view', name='logout'),
    url(r'^register/?$', 'register', name='register'),
)

